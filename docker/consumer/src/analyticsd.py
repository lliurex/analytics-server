import functools
import logging
import logging.config
import time
import pika
import os
import signal
import threading
import queue
import json
import mysql.connector
from mysql.connector import errorcode
import hashlib
import traceback
import datetime

MONITOR_FILE = '/tmp/analtytics-status-file'

LOG_LEVEL       = os.environ.get('LOG_LEVEL','NOTSET')
RABBITUSER      = os.environ.get('RABBIT_USER','analytics')
RABBITPASSWORD  = os.environ.get('RABBIT_PASSWORD','analytics')
RABBITHOST      = os.environ.get('RABBIT_HOST','queue')
RABBITPORT      = os.environ.get('RABBIT_PORT',5672)
RABBITVHOST     = os.environ.get('RABBIT_VHOST','/')
RABBITEXCHANGE  = os.environ.get('RABBIT_EXCHANGE','analytics')
RABBITEXCHANGE_TYPE = os.environ.get('RABBIT_EXCHANGE_TYPE','direct')
RABBITQUEUE     = os.environ.get('RABBIT_QUEUE','analytics')
RABBITROUTINGKEY= os.environ.get('RABBIT_ROUTING_KEY','analytics')
MYSQL_DATABASE  = os.environ.get('MYSQL_DATABASE','analytics')
MYSQL_USER      = os.environ.get('MYSQL_USER','analytics')
MYSQL_PASSWORD  = os.environ.get('MYSQL_PASSWORD','analytics')
MYSQL_HOST      = os.environ.get('MYSQL_HOST','db')

def runningInDocker():
    with open('/proc/self/cgroup', 'r') as procfile:
        for line in procfile:
            fields = line.strip().split('/')
            if fields[1] == 'docker':
                return True

standalone = not runningInDocker()
if standalone:
    LOG_LEVEL  = 'DEBUG'
    RABBITHOST = 'localhost'
    MYSQL_HOST = 'localhost'

log = logging.getLogger('analyticsd')
if not LOG_LEVEL or not isinstance(LOG_LEVEL,str) or LOG_LEVEL.upper() not in list(logging._levelToName.values()):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    })
    _LOG_LEVEL = 'NOTSET'
    log = logging
else:
    _LOG_LEVEL = logging._nameToLevel.get(LOG_LEVEL.upper())
    handler = logging.StreamHandler()
    log.setLevel(_LOG_LEVEL)
    log.addHandler(handler)

signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items())) if v.startswith('SIG') and not v.startswith('SIG_'))

class QueueConsumer(object):
    FORCE_ACK_TIME = 60
    def __init__(self, amqp_url):
        self._thread = None
        self.should_reconnect = False
        self.was_consuming = False
        self._reconnect_delay = 0
        self.status = False
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self._consuming = False
        self._received = {}
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 100
        self._process_cb = None
        self._last_ack_time = None
        self._last_tag = None
        self._flush_thread = threading.Thread(name='Flush thread',target=self.force_flush)
        self._flush_thread.setDaemon(True)
        self._last_tag_acked = 0

    def connect(self):
        log.info('Connecting to queue: {}'.format(self._url))
        return pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if not self._connection:
            log.info("Can't close connection, not initialized")
        else:
            if self._connection.is_closing or self._connection.is_closed:
                log.info('Connection is closing or already closed')
            else:
                log.info('Closing connection')
                self._connection.close()

    def on_connection_open(self, _unused_connection):
        log.info('Queue connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        log.error('Queue connection open failed, trying to reconnect: {}'.format(err))
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        self.status = False
        if self._closing:
            self._received = {}
            self._connection.ioloop.stop()
            self._connection = None
        else:
            log.warning('Connection closed, reconnect necessary: {}'.format(reason))
            self.reconnect()

    def reconnect(self):
        self.should_reconnect = True
        self.status = False
        log.info('Mark reconnection needed')
        self._connection.ioloop.stop()
        log.info('Reconnectig: stop ioloop done')
        # self.stop()
    
    def _reconnect(self):
        self.close_connection()
        self._connection = self.connect()

    def open_channel(self):
        log.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        log.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(RABBITEXCHANGE)

    def add_on_channel_close_callback(self):
        log.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        log.warning('Channel {} was closed: {}'.format(channel,reason))
        self.close_connection()

    def setup_exchange(self, exchange_name):
        if exchange_name != '':
            log.info('Declaring exchange: {}'.format(exchange_name))
            cb = functools.partial(
                self.on_exchange_declareok,
                userdata=exchange_name
            )
            self._channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=RABBITEXCHANGE_TYPE,
                callback=cb
            )
        else:
            self._connection.ioloop.call_later(0,self.on_exchange_declareok)

    def on_exchange_declareok(self, _unused_frame=None, userdata=None):
        if userdata:
            log.info('Using default exchange')
        else:
            log.info('Exchange declared: {}'.format(userdata))
        self.setup_queue(RABBITQUEUE)

    def setup_queue(self, queue_name):
        log.info('Declaring queue {}'.format(queue_name))
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name, callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):
        queue_name = userdata
        log.debug('Binding {} to {} with {}'.format(
            RABBITEXCHANGE,
            queue_name,
            RABBITROUTINGKEY
            )
        )
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        if RABBITEXCHANGE:
            self._channel.queue_bind(
                queue_name,
                RABBITEXCHANGE,
                routing_key=RABBITROUTINGKEY,
                callback=cb
            )
        else:
            self._connection.ioloop.call_later(0,cb)

    def on_bindok(self, _unused_frame=None, userdata=None):
        if userdata:
            log.info('Queue bound: {}'.format(userdata))
        else:
            log.info('Using default exchange, bind not needed')
        self.set_qos()

    def set_qos(self):
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count,
            callback=self.on_basic_qos_ok
        )

    def on_basic_qos_ok(self, _unused_frame):
        log.info('QOS set to: {}'.format(self._prefetch_count))
        self.start_consuming()

    def start_consuming(self):
        log.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            RABBITQUEUE, 
            self.on_message
        )
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        log.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        log.debug('Consumer was cancelled remotely, shutting down: {}'.format(method_frame))
        if self._channel:
            self._channel.close()

    def setProcessMethod(self,cb=None):
        if cb and hasattr(cb,'__call__'):
            self._process_cb = cb
            log.info("Setting process method '{}' for queue content".format(cb.__name__))
        else:
            log.error('Wrong process method for queue content, not applying')

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        # log.debug('Received message # {} from {}: {}'.format(
        #     basic_deliver.delivery_tag,
        #     properties.app_id,
        #     body
        #     )
        # )

        log.debug('Received message # {}'.format(basic_deliver.delivery_tag))
        self._received.setdefault(basic_deliver.delivery_tag,(time.time(),body))
        self._last_tag = basic_deliver.delivery_tag
        if len(self._received) == self._prefetch_count:
            self._send_to_cb()
            self.acknowledge_message(basic_deliver.delivery_tag)

    def _send_to_cb(self):
        if self._process_cb:
            self._process_cb([v[1] for k,v in self._received.items()])
            self._received = {}
            log.info('Flushing queue content')

    def force_flush(self):
        if not self._last_ack_time:
            self._last_ack_time = time.time()
        while not self._closing:
            if time.time() > self._last_ack_time + self.FORCE_ACK_TIME:
                log.info('Forcing flush')
                if self._last_tag == self._last_tag_acked:
                    log.info('No new messages, skipping force flush')
                else:
                    try:
                        self._send_to_cb()
                        self.acknowledge_message(self._last_tag)
                    except Exception as e:
                        log.error('Error forcing flush, {}'.format(e))
                        self.status = False
                self._last_ack_time = time.time()
            time.sleep(1)

    def acknowledge_message(self, delivery_tag):
        log.info('Acknowledging message {}'.format(delivery_tag))
        self._last_ack_time = time.time()
        multiple = self._prefetch_count != 1 
        self._channel.basic_ack(delivery_tag,multiple)
        self._last_tag_acked = delivery_tag 

    def stop_consuming(self):
        if self._channel:
            log.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, 
                userdata=self._consumer_tag
            )
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        self._consuming = False
        log.info('RabbitMQ acknowledged the cancellation of the consumer: {}'.format(userdata))
        self.close_channel()

    def close_channel(self):
        log.info('Closing the channel')
        self._channel.close()
        self.status = False

    def run(self):
        self._flush_thread.start()
        while not self._closing:
            log.debug('Queueloop')
            try:
                self._received = {}
                if not self._connection:
                    self._connection = self.connect()
                self.status = True
                log.debug('Ioloop START')
                self._connection.ioloop.start()
                log.debug('Ioloop END')
                self.status = False
            except KeyboardInterrupt:
                self.status = False
                log.warning('{} interrupted'.format(self.__name__))
            except Exception as e:
                self.status = False
                log.warning('{} interrupted, {}'.format(self.__name__,e))
            if self.should_reconnect:
                reconnect_delay = self._get_reconnect_delay()
                log.info('Reconnecting after {} seconds'.format(reconnect_delay))
                time.sleep(reconnect_delay)
                self._reconnect()

    def _get_reconnect_delay(self):
        if self.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay
    
    def start(self):
        if not self._thread:
            self._thread = threading.Thread(name='QueueConsumer', target=self.run)
            self._thread.setDaemon(True)
            self._thread.start()

    def stop(self):
        if not self._closing:
            self._closing = True
            self.status = False
            log.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            log.info('Stopped')

class Client(object):
    def __init__(self,**kwargs):
        self._nullable_fields = ['arch','mem','vga','cpu','ncpu','mode']
        self._boolean_fields = ['ltsp']
        self._integer_fields = ['uuid','mem','ncpu']
        self._string_fields = ['Client_uid','string_release','Releases_name','date','string_flavour','Flavours_name','arch','vga','cpu','mode']
        self.uuid = None
        self.Client_uid = kwargs.get('uid',None)
        self.string_release = kwargs.get('vers',None)
        if self.string_release:
            self.Releases_name = self._normalize_release(self.string_release)
        else:
            self.Releases_name = None
        self._date_format = '%Y-%m-%d %H:%M:%S'
        self.date = kwargs.get('date',None)
        if self.date:
            self._date = self._normalize_date(self.date) 
        else:
            self._date = None
        self.string_flavour = kwargs.get('sab',None)
        if self.string_flavour:
            self.Flavours_name = self._normalize_flavour(self.Releases_name,self.string_flavour)
        else:
            self.Flavours_name = None
        specs = kwargs.get('specs',{})
        self.arch = specs.get('arch',None)
        self._mac = specs.get('mac',None)
        self.mem = specs.get('mem',None)
        self.vga = specs.get('vga',None)
        cpu = specs.get('cpu',{})
        subtype = specs.get('subtype',{})
        self.cpu = cpu.get('model',None)
        self.ncpu = cpu.get('ncpus',None)
        self.ltsp = subtype.get('LTSP',None)
        self.mode = subtype.get('MODE',None)
        self._fn_db_string = lambda x : "'{}'".format(x)
        self._fn_db_integer = lambda x : str(x)
        self._fn_db_boolean = lambda x : '1' if x is True or x == 1 or x.lower() == 'true' else '0'
        self._mandatory_keys = [ x for x in self._string_fields + self._integer_fields if x not in self._nullable_fields ]
        self.check_definitions()

    def validate(self, client=None, skip=[]):
        if not client:
            client = self
        try:
            if not isinstance(client,Client):
                return False
            for k in self._mandatory_keys:
                if k in skip:
                    continue
                if not hasattr(client,k) or not getattr(client,k,None):
                    return False
            return True
        except Exception as e:
            raise e

    def check_definitions(self):
        l = self._string_fields + self._integer_fields + self._boolean_fields
        l2 = list(self.get_fields())
        res = [ x for x in l2 if x not in l ]
        if not res:
            return True
        else:
            err = "'{}' not in field type definitions".format(','.join(res))
            log.error(err)
            raise Exception(err)

    def get_fields(self):
        for k in sorted(self.__dict__.keys()):
            if k[0] != '_':
                yield k

    def get_values(self):
        for k in self.get_fields():
            yield getattr(self,k)

    def print_sql_tuple(self):
        names = list(self.get_fields())
        i=0
        l=[]
        for v in self.get_values():
            if names[i] in self._string_fields:
                l.append(self._fn_db_string(v))
            elif names[i] in self._integer_fields:
                l.append(self._fn_db_integer(v))
            elif names[i] in self._boolean_fields:
                l.append(self._fn_db_boolean(v))
            i+=1
        return '({})'.format(','.join(l))
    
    def _normalize_date(self, date=None):
        # d=datetime.today()+relativedelta(months=-1)
        # d.strftime('%Y-%m-%d %H:%M:%S')
        if not date:
            log.debug('Empty date when normalizing')
            return None
        return datetime.datetime.strptime(date,self._date_format)

    def _normalize_release(self, release=None):
        if not release:
            log.debug('Empty release when normalizing')
            return None

        if release[0:2] in ['15','16','19','21']:
            return release[0:2]
        else:
            return 'other'

    def _normalize_flavour(self, release=None, flavour=None):
        if not release or not flavour:
            log.debug('Empty flavour when normalizing')
            return None

        if release == '15':
            if 'server' not in flavour and 'client' not in flavour and 'desktop' in flavour:
                return 'desktop'
            elif 'server' in flavour:
                return 'server'
            elif 'client' in flavour:
                return 'client' 
        elif release in ['16','19','21']:
            if 'server' in flavour:
                return 'server'
            elif 'client' in flavour:
                return 'client'
            elif 'desktop' in flavour:
                return 'desktop'
        return 'other'

class App(object):
    def __init__(self,**kwargs):
        self._integer_fields = ['uuid','count']
        self._string_fields = ['Releases_name','date','Flavours_name','string']
        self._boolean_fields = []
        self.uuid = None
        self._date = None
        self.date = None
        self.Releases_name = None
        self.Flavours_name = None
        self.string = None
        self.count = 0
        self._fn_db_string = lambda x : "'{}'".format(x)
        self._fn_db_integer = lambda x : str(x)
        self._fn_db_boolean = lambda x : '1' if x is True or x == 1 or x.lower() == 'true' else '0'
        self.check_definitions()

    def check_definitions(self):
        l = self._string_fields + self._integer_fields + self._boolean_fields
        l2 = list(self.get_fields())
        res = [ x for x in l2 if x not in l ]
        if not res:
            return True
        else:
            err = "'{}' not in field type definitions".format(','.join(res))
            log.error(err)
            raise Exception(err)

    def get_fields(self):
        for k in sorted(self.__dict__.keys()):
            if k[0] != '_':
                yield k

    def get_values(self):
        for f in self.get_fields():
            yield getattr(self,f)
    
    def print_sql_tuple(self):
        names = list(self.get_fields())
        i=0
        l=[]
        for v in self.get_values():
            if names[i] in self._string_fields:
                l.append(self._fn_db_string(v))
            elif names[i] in self._integer_fields:
                l.append(self._fn_db_integer(v))
            elif names[i] in self._boolean_fields:
                l.append(self._fn_db_boolean(v))
            i+=1
        return '({})'.format(','.join(l))

class Acumulator(object):
    def __init__(self):
        self.apps = {}
        self.clients = {}
        self._mutex = threading.Lock()
        self._uuid_db = {}
    
    def _get_uuid_string(self,*args,**kwargs):
        return '-'.join([str(x) for x in args])

    def _get_hash(self,string):
        return int(hashlib.sha1(string.encode('utf-8')).hexdigest()[0:16],16)

    def _gen_uuid(self,*args,**kwargs):
        try:
            string=self._get_uuid_string(*args)
            self._uuid_db.setdefault(string,self._get_hash(string))
            return self._uuid_db.get(string)
        except Exception as e:
            log.error(traceback.format_exc(),'critical')
    
    def _make_attributes_for_db(self,client):
        for f in client._nullable_fields:
            if not getattr(client,f):
                setattr(client,f,'NULL')
        for f in client._boolean_fields:
            if not getattr(client,f):
                setattr(client,f,'FALSE')
            else:
                setattr(client,f,'TRUE')
        for attr in client.get_fields():
            if not isinstance(getattr(client,attr),str):
                setattr(client,attr,str(getattr(client,attr)))

    def add(self,*args,**kwargs):
        if kwargs.get('healthcheck',None):
            return None
        client = Client(**kwargs)
        if not client.validate(skip=['uuid']):
            return False

        string = self._get_uuid_string(
            client._date.month,
            client._date.year,
            client.Client_uid,
            client.Releases_name,
            client.Flavours_name,
            client.mode
        )
        self._mutex.acquire()
        found = self.clients.get(string,None)
        if not found:
            client.uuid = self._gen_uuid(
                client._date.month,
                client._date.year,
                client.Client_uid,
                client.Releases_name,
                client.Flavours_name,
                client.mode
            )
            self._make_attributes_for_db(client)
            self.clients.setdefault(client.uuid,client)
        for appname,appvalue in kwargs.get('stats',{}).items():
            try:
                string = self._get_uuid_string(
                    client._date.month,
                    client._date.year,
                    client.Releases_name,
                    client.Flavours_name,
                    appname
                )
                found = self.apps.get(string,None)
                if found:
                    app = found
                    app.count += int(appvalue)
                else:
                    app = App()
                    app._date = client._date
                    app.date = client.date
                    app.Releases_name = client.Releases_name
                    app.Flavours_name = client.Flavours_name 
                    app.uuid = self._gen_uuid(
                        app._date.month,
                        app._date.year,
                        app.Releases_name,
                        app.Flavours_name,
                        appname
                    )
                    app.string = appname
                    app.count = int(appvalue)
                    self.apps.setdefault(string,app)
            except Exception as e:
                continue
        self._mutex.release()
        return True

    def get_values(self):
        lc=[]
        la=[]
        self._mutex.acquire()
        for kc,c in self.clients.items():
            lc.append(c.print_sql_tuple())
        for ka,a in self.apps.items():
            la.append(a.print_sql_tuple())
        self.clients = {}
        self.apps = {}
        self._mutex.release()
        return (lc,la)

class AnalyticsDatabase(object):
    def __init__(self, user=None, password=None, host=None, database=None ):
        self._user = user
        self._password = password
        self._host = host
        self._database = database
        self._connection = None
        self._cursor = None
        self._app_obj = App()
        self._client_obj = Client()
        self._mutex = threading.Lock()

    def connect(self,user=None,password=None,host=None,database=None):
        if user and password and host and database:
            self._user = user
            self._password = password
            self._host = host
            self._database = database

        if self._connection:
            log.warning('Connecting with active connection, disconecting first')
            self.disconnect()
        try:
            self._connection = mysql.connector.connect(user=self._user,password=self._password,host=self._host,database=self._database)
            log.info('Database connection done!')
        except mysql.connector.Error as e:
            self._log_mysql_error(e)
            self._connection = None
        except:
            log.error('Unknown database error when connecting')
            self._connection = None
        if self._connection:
            self.set_autocommit(False)
            self._cursor = self.get_cursor()

    def _log_mysql_error(self, e):
        if not hasattr(e,'errno'):
            log.error('Wrong MySQL error when trying to log')
            return None
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            log.error('MySQL connector error, wrong username/password')
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            log.error('MySQL connector error, wrong database')
        elif e.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            log.error('Mysql connector error, table already exists')
        else:
            log.error('Unknown MySQL error: {}'.format(e))

    def _set_isolation(self):
        if self.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"):
            log.debug('Set database isolation level')
        else:
            log.error('Error setting database isolation level')

    def set_autocommit(self,use_autocommit):
        if not self._connection:
            self.connect()
        if self._connection:
            self._connection.autocommit = use_autocommit
            log.debug('Setting autocommit to {}'.format(use_autocommit))
    
    def get_cursor(self):
        if not self._connection:
            self.connect()
        else:
            try:
                cur = self._connection.cursor()
                log.debug('Getting cursor from connection')
                return cur
            except Exception as e:
                log.error('Error getting database cursor, {}'.format(e))
        return None

    def disconnect(self):
        if self._connection:
            try:
                self._connection.close()
                log.warning('Connection closed')
            except Exception as e:
                log.warning('Error when disconnecting, {}'.format(e))
            log.info('Disconnecting from database')
            self._connection = None
            self._cursor = None

    def execute(self, statement, cursor=None):
        if not self._connection or not self._cursor:
            self.connect()
        if not cursor:
            if self._cursor:
                cursor = self._cursor
            else:
                log.error('Cursor not available when executing {}'.format(statement))
                return None
        retry = 1
        done = False
        ex = None
        while retry and not done:
            try:
                self._mutex.acquire()
                self._cursor.execute(statement)
                log.info('Execution into db succeded')
                # log.info(statement)
                self._mutex.release()
                done = True
            except mysql.connector.Error as e:
                self._log_mysql_error(e)
                retry -= 1
                ex = e
            except Exception as e:
                log.error("Error when executing, {}".format(e))
                retry -= 1
                ex = e
        if not done:
            raise ex
        return done

    def insert_client_values(self, lvalues):
        if not lvalues:
            return
        escape = lambda x : "`{}`".format(x)
        self.execute("INSERT INTO Client_Versions({}) VALUES {} ON DUPLICATE KEY UPDATE uuid=uuid ;".format(
            ','.join(map(escape,self._client_obj.get_fields())),
            ','.join(lvalues)
        ))

    def commit(self):
        if self._connection:
            self._connection.commit()
            log.info('Commited data')
    
    def start_transaction(self):
        if self._connection:
            self.execute("START TRANSACTION;")
            log.info('Transaction start')

    def rollback(self):
        if self._connection:
            self._connection.rollback()
            log.info('Data rolled back')

    def insert_apps_values(self, lvalues):
        if not lvalues:
            return
        escape = lambda x : "`{}`".format(x)
        self.execute("INSERT INTO RecvPackages({}) VALUES {} ON DUPLICATE KEY UPDATE count = count + VALUES(count) ;".format(
            ','.join(map(escape,self._app_obj.get_fields())),
            ','.join(lvalues)
        ))

class Analyticsd(object):
    PROCESSOR_TIME = 1
    DUMP_DATABASE_TIME = 30

    def __init__(self):
        self._thread = threading.Thread(name='Analyticsd processor',target=self._processor)
        self._thread_db = threading.Thread(name='Analyticsd database',target=self._processor_database)
        self._thread.setDaemon(True)
        self._thread_db.setDaemon(True)
        self._mutex = threading.Lock()
        self._workQueue = queue.Queue()
        self._acumulator = Acumulator()
        self._db = AnalyticsDatabase()
        self._exitting = False
        self.status_proc = False
        self.status_db = False

    def process(self,*args,**kwargs):
        a=1
        self._mutex.acquire()
        for i in args[0]:
            try:
                if not i:
                    continue;
                self._workQueue.put(json.loads(i.decode('utf-8')))
            except Exception as e:
                log.warning('invalid message! skipping')
        self._mutex.release()
    
    def start(self):
        self._thread.start()
        self._db.connect(MYSQL_USER,MYSQL_PASSWORD,MYSQL_HOST,MYSQL_DATABASE)
        self._thread_db.start()

    def stop(self):
        self._db.disconnect()
        self._exitting = True

    def _processor(self):
        while not self._exitting:
            self.status_proc = True
            if not self._workQueue.empty():
                ok=0
                nok=0
                health=0
                while not self._workQueue.empty():
                    self._mutex.acquire()
                    i = self._workQueue.get()
                    self._mutex.release()
                    try:
                        res = self._acumulator.add(**i)
                        if res == True:
                            ok+=1
                        elif res == None:
                            health+=1
                        else:
                            nok+=1
                    except Exception as e:
                        log.error('Error acumulating workqueue item, {}'.format(e))
                        nok+=1
                        continue
                log.info('Acumulating messages: (ok/nok/health {}/{}/{})'.format(ok,nok,health))
            time.sleep(self.PROCESSOR_TIME)
        self.status_proc = False
    
    def _processor_database(self):
        while not self._exitting:
            clients, apps = self._acumulator.get_values()
            self.status_db = True
            if clients and apps:
                log.info('Preparing for insert {} clients {} apps'.format(len(clients),len(apps)))
                try:
                    self._db.start_transaction()
                    self._db.insert_client_values(clients)
                    self._db.insert_apps_values(apps)
                    self._db.commit()
                except Exception as e:
                    log.error('Error inserting, {}'.format(e))
                    self._db.rollback()
            time.sleep(self.DUMP_DATABASE_TIME)
        self.status_db = False

class HealthMonitor(object):
    def __init__(self,queuec,analytics):
        global MONITOR_FILE
        self._check_time = 30
        self._monitor_file = MONITOR_FILE
        self._queue = queuec
        self._analytics = analytics
        self._thread = None
        self._monitor_threads = []
        self._monitor_threads.append(self._queue._thread)
        self._monitor_threads.append(self._queue._flush_thread)
        self._monitor_threads.append(self._analytics._thread)
        self._monitor_threads.append(self._analytics._thread_db)

    def start(self):
        log.info('HealthMonitor starting, checking time={}'.format(self._check_time))
        if not self._thread:
            self._thread = threading.Thread(name='HealthMonitor',target=self.monitor)
            self._thread.start()

    def monitor(self):
        global running
        while running:
            try:
                status = True
                main_status = running
                queue_status = self._queue.status
                analytics_db_status = self._analytics.status_db
                analytics_proc_status = self._analytics.status_proc
                for t in self._monitor_threads:
                    if not t.is_alive():
                        status = False
                        break
                status = status and main_status and queue_status and analytics_db_status and analytics_proc_status
                log.info('HealthMonitor: status is {}'.format(status))
                with open(self._monitor_file,'w') as fp:
                    fp.write('{}'.format(status))
            except Exception as e:
                log.error('Exception HealthMonitor: {}'.format(e))
            time.sleep(self._check_time)
        os.remove(self._monitor_file)

def exitting(*args,**kwargs):
    if args:
        signum,sigframe = args
        log.debug('Exitting by signal {}\nFrame:\n{}\n'.format(signames.get(signum),sigframe))
        if signum == 10:
            log.info('Killed from docker, healthcheck failed!')
    else:
        log.info('Exitting called')
    global queuec, running, analyticsd
    queuec.stop()
    analyticsd.stop()
    running = False

def main():
    global running,queuec,analyticsd
    amqp_url = 'amqp://{}:{}@{}:{}/{}?connection_attempts=3&heartbeat=3600'.format(
                RABBITUSER,
                RABBITPASSWORD,
                RABBITHOST,
                RABBITPORT,
                RABBITVHOST.replace('/','%2F')
            )

    log.info('Starting Analyticsd')
    signal.signal(signal.SIGTERM,exitting)
    signal.signal(signal.SIGQUIT,exitting)
    signal.signal(signal.SIGUSR1,exitting)

    running = True

    queuec = QueueConsumer(amqp_url)
    analyticsd = Analyticsd()
    queuec.setProcessMethod(analyticsd.process)
    analyticsd.start()
    queuec.start()
    monitor = HealthMonitor(queuec,analyticsd)
    monitor.start()
    try:
        i=None
        while running:
            if not i:
                i=10
                log.info('Analyticsd: QueueConsumer/Processor/Database: {}/{}/{}'.format(
                    queuec.status,
                    analyticsd.status_proc,
                    analyticsd.status_db
                ))
            i-=1
            time.sleep(1)
    except Exception as e:
        log.info('Exception mainthread Analtytics ({}), exitting'.format(e))
        exitting()
        

if __name__ == '__main__':
    main()