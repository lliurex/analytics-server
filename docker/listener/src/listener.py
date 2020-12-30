import threading
import time
import sys
import os
import functools
import logging
import logging.config
import signal
import json
import datetime

import pika

from flask import Flask,Response,make_response,request,jsonify,json
from flask.views import MethodView

LOG_LEVEL       = os.environ.get('LOG_LEVEL','NOTSET')
LISTENERHOST    = '0.0.0.0'
LISTENERPORT    = os.environ.get('LISTENER_PORT',80)
RABBITUSER      = os.environ.get('RABBIT_USER','analytics')
RABBITPASSWORD  = os.environ.get('RABBIT_PASSWORD','analytics')
RABBITHOST      = os.environ.get('RABBIT_HOST','queue')
RABBITPORT      = os.environ.get('RABBIT_PORT',5672)
RABBITVHOST     = os.environ.get('RABBIT_VHOST','/')
RABBITEXCHANGE  = os.environ.get('RABBIT_EXCHANGE','')
RABBITQUEUE     = os.environ.get('RABBIT_QUEUE','analytics')
RABBITROUTINGKEY= os.environ.get('RABBIT_ROUTING_KEY','analytics')

def runningInDocker():
    with open('/proc/self/cgroup', 'r') as procfile:
        for line in procfile:
            fields = line.strip().split('/')
            if fields[1] == 'docker':
                return True

standalone = not runningInDocker()
if standalone:
    LOG_LEVEL = 'DEBUG'
    RABBITHOST      = 'localhost'
    LISTENERPORT    = 8080

log = logging.getLogger('ListenerApp')
if not LOG_LEVEL or not isinstance(LOG_LEVEL,str) or LOG_LEVEL.upper() not in list(logging._levelToName.values()):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        }
    )
    _LOG_LEVEL = 'NOTSET'
    log = logging
else:
    _LOG_LEVEL = logging._nameToLevel.get(LOG_LEVEL.upper())
    handler = logging.StreamHandler()
    log.setLevel(_LOG_LEVEL)
    log.addHandler(handler)

mutex = threading.Lock()

class AnalyticsReceiver(object):
    @staticmethod
    def _validateMessage(data):
        mandatory_keys = ['vers','sab','uid','stats']
        try:
            if not isinstance(data,dict):
                raise Exception()
            for k in mandatory_keys:
                if not data.get(k,''):
                    raise Exception("Missing '{}' key on data".format(k))
                if k == 'stats':
                    stats = data.get(k,'None')
                    if isinstance(stats,str):
                        stats = json.loads(stats)
                        data[k] = stats
                    if isinstance(stats,dict):
                        for sk,sv in stats.items():
                            if not isinstance(sk,str) and isinstance(sv,str):
                                raise Exception('Wrong stats value')
        except Exception as e:
            raise e

    @staticmethod
    def _buildMessage(data):
        keys = ['vers','sab','uid','stats','specs','date']
        d = dict()
        try:
            for k in [ dk for dk in data.keys() if dk not in data.keys() ]:
                data.setdefault(k,None)
            if not data.get('date'):
                data['date']=datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        except:
            raise Exception()
        return data

    @staticmethod
    def makeMessage(data):
        try:
            post = json.loads(data)
            AnalyticsReceiver._validateMessage(post)
            message = AnalyticsReceiver._buildMessage(post)
            message = json.dumps(message,separators=(',',':'))
            return ('OK', message)
        except Exception as e:
            log.debug('{}'.format(e))
            return ('NOK',)

class QueueManager(object):
    RECONNECTION_TIME = 1
    EXCHANGE = RABBITEXCHANGE
    EXCHANGE_TYPE = 'direct'
    PUBLISH_INTERVAL = 0
    QUEUE = RABBITQUEUE
    ROUTING_KEY = RABBITROUTINGKEY
    WITH_CONFIRMATIONS = True
    WAIT_TIME = 30

    def __init__(self,url=None):
        self._monitor_thread = None
        self._connection = None
        self._channel = None
        self._deliveries = {}
        self._acked = None
        self._nacked = None
        self._message_number = None
        self._stopping = False
        self._pause = False
        self._url = None
        if url:
            self._url = url
        self._thread_queue = None
        self._health = []
        self._last_healthcheck = None
        log.debug('New Quemanager')

    def connect(self,url=None):
        if url:
            self._url = url
        connection = pika.SelectConnection(
            pika.URLParameters(self._url),
            on_open_callback = self.on_connection_open,
            on_open_error_callback = self.on_connection_open_error,
            on_close_callback = self.on_connection_closed
        )
        log.info('Oppening connection to queue {}'.format(self._url))
        return connection

    def on_connection_open(self, _unused_connection):
        log.info('Connection opened')
        self.add_on_connection_blocked_callback()
        self.add_on_connection_unblocked_callback()
        self.open_channel()

    def add_on_connection_blocked_callback(self):
        log.warning('Connection is BLOCKED')
        self.PUBLISH_INTERVAL+=1
        self._pause = True

    def add_on_connection_unblocked_callback(self):
        log.warning('Connection is UNblocked')
        self.PUBLISH_INTERVAL=0
        self._pause = False

    def on_connection_open_error(self, _unused_connection, err):
        log.error('Fail oppening connection, {}, retry in {} seconds'.format(err,self.RECONNECTION_TIME))
        self._connection.ioloop.call_later(self.RECONNECTION_TIME, self._connection.ioloop.stop)

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        if self._stopping:
            self._connection.ioloop.stop()
        else:
            log.warning('Connection unexpectedly closed, {}, retry in {} seconds'.format(reason, self.RECONNECTION_TIME))
            self._connection.ioloop.call_later(self.RECONNECTION_TIME, self._connection.ioloop.stop)

    def open_channel(self):
        log.info('Creating new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        log.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        log.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        log.warning('Channel was closed !!!, {}'.format(reason))
        self._channel = None
        if not self._stopping:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        if not exchange_name:
            log.info('Using default exchange')
            self.EXCHANGE="analytics"
            self._connection.ioloop.call_later(0,self.on_exchange_declareok)
        else:        
            log.info('Declaring exchange {}'.format(exchange_name))
            if exchange_name:
                cb = functools.partial(self.on_exchange_declareok, userdata=exchange_name)
                self._channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=self.EXCHANGE_TYPE,
                    callback=cb
                )

    def on_exchange_declareok(self, _unused_frame=None, userdata=None):
        if userdata:
            log.info('Exchange {} declared'.format(userdata))
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        log.info('Declaring queue {}'.format(queue_name))
        self._channel.queue_declare(
            queue=queue_name, 
            callback=self.on_queue_declareok
        )

    def on_queue_declareok(self, _unused_frame):
        log.info('Binding queue {} with exchange {} using routing key {}'.format(self.QUEUE,self.EXCHANGE_TYPE,self.ROUTING_KEY))
        self._channel.queue_bind(
            self.QUEUE,
            self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bindok
        )

    def on_bindok(self, _unused_frame):
        log.info('Queue bound')
        self.start_publishing()

    def start_publishing(self):
        log.info('Issuing consumer related RPC commands')
        if self.WITH_CONFIRMATIONS:
            log.info('Using confirmations')
            self.enable_delivery_confirmations()
        self.schedule_next_message()

    def enable_delivery_confirmations(self):
        log.info('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        log.debug('Received {} for delivery tag: {}'.format(confirmation_type,method_frame.method.delivery_tag))

        mutex.acquire()
        
        if method_frame.method.multiple:
            deliveries = [ k for k in self._deliveries.keys() if k <= method_frame.method.delivery_tag ]
        else:
            deliveries = [ method_frame.method.delivery_tag ]
        
        if confirmation_type == 'ack':
            self._acked += len(deliveries)
            log.debug('Received ack number: {}, current length of deliveries: {}'.format(method_frame.method.delivery_tag,len(self._deliveries)))
            for k in deliveries:
                if k == self._last_healthcheck:
                    self._healthcheck(k)
                del self._deliveries[k]
        elif confirmation_type == 'nack':
            self._nacked += len(deliveries)
            log.debug('Received Nack number: {}, current length of deliveries: {}'.format(method_frame.method.delivery_tag,len(self._deliveries)))
        mutex.release()

        log.debug(
            'Published {} messages, {} have yet to be confirmed, {} were acked and {} were nacked'.format(
                self._message_number,
                len(self._deliveries),
                self._acked,
                self._nacked
            )
        )
        if method_frame.method.delivery_tag == 1:
            log.info('QueueManager initialization complete')

    def schedule_next_message(self,message={},headers={},inc=0):
        log.debug('Scheduling called')
        cb = functools.partial(self.publish_message,headers=headers,message=message)
        log.debug('Scheduled next message')
        self._connection.ioloop.call_later(
            self.PUBLISH_INTERVAL+inc,
            cb
        )

    def publish_message(self, message={},headers={}):
        log.debug("Publishing message '{}'".format(message))
        if self._channel is None or not self._channel.is_open:
            log.error('Channel closed when publishing, requeuing...')
            self.schedule_next_message(message=message,headers=headers)
            return
        properties = pika.BasicProperties(
            app_id='QueueManager',
            content_type='application/json',
            headers=headers
        )
        self._channel.basic_publish(
            self.EXCHANGE,
            self.ROUTING_KEY,
            message,
            properties   
        )
        log.debug('Published message #{}'.format(self._message_number))
        self._message_number += 1
        self._deliveries.setdefault(self._message_number,(time.time(),message))
        return self._message_number

    def _healthcheck(self,received=None):
        if received:
            if received == self._last_healthcheck and \
                self._monitor_thread.is_alive() and \
                self._thread_queue.is_alive() and \
                self._connection.is_open and \
                self._channel.is_open:

                self._health.append(True)
            else:
                self._health.append(False)
            if len(self._health) > 3:
                self._health=self._health[-3:]
        else:
            if self._connection and \
                self._connection.is_open and \
                self._channel and \
                self._channel.is_open:
                
                self._last_healthcheck_message=time.time()
                self._last_healthcheck = self.publish_message(message=json.dumps({'healthcheck':self._last_healthcheck_message}))

    def healthcheck(self):
        for x in self._health:
            if x:
                return True
        return False

    def monitor(self):
        while not self._stopping:
            log.debug('Run retries {}'.format(len(self._deliveries)))
            self._healthcheck()
            log.debug('QueueManager health: {}'.format('Good' if self._health else 'Fail'))
            time.sleep(int(self.WAIT_TIME/3))
            try:
                mutex.acquire()
                to_do = [ k for k in self._deliveries.keys() if self._deliveries[k][0] < time.time() - self.WAIT_TIME ]
                i=0
                ltodo = len(to_do)
                ldelivery = len(self._deliveries)
                for m in to_do:
                    i+=0.1
                    self.schedule_next_message(message=self._deliveries[m][1],inc=i)
                    del self._deliveries[m]
                if ltodo:
                    log.warning('Retrying {} messages from {} pending'.format(ltodo,ldelivery))
                mutex.release()
            except Exception as e:
                log.error('Error on retries thread, {}'.format(e))

    def start(self,url=None):
        if url:
            self._url = url
        log.info('Starting QueueManager threads')
        if not self._thread_queue:
            self._thread_queue = threading.Thread(name='QueueManager', target=self.run)
            self._thread_queue.setDaemon(True)
            self._thread_queue.start()
        if not self._monitor_thread:
            self._monitor_thread = threading.Thread(name='Monitor_deliveries',target=self.monitor)
            self._monitor_thread.setDaemon(False)
            self._monitor_thread.start()

    def run(self):
        while not self._stopping:
            self._connection = None
            self._deliveries = {}
            self._acked = 0
            self._nacked = 0
            self._message_number = 0
            try:
                self._connection = self.connect()
                # Blocking call
                log.debug('QueueManager running')
                self._connection.ioloop.start()
                log.warning('Exitting from QueueManager processing loop')
            except pika.exceptions.AMQPConnectionError:
                log.warning('Connection not available, waiting...')
            except socket.gaierror:
                log.warning("Host '{}' down, waiting...".format(RABBITHOST))
            except Exception as e:
                log.error('Error on Queuemanager thread, {}, exitting...'.format(e))
                self.stop()
                if (self._connection is not None and not self._connection.is_closed):
                    # Blocking call, allow trigger disconnection rpc commands
                    self._connection.ioloop.start()
        log.info('QueueManager Stopped')

    def stop(self):
        log.warning('Stopping QueueManager')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        if self._channel is not None:
            log.debug('Closing channel')
            self._channel.close()

    def close_connection(self):
        if self._connection is not None:
            log.debug('Closing connection')
            self._connection.close()

class ListenerRequest(MethodView):
    def __init__(self, *args, **kwargs):
        self._cb = kwargs.get('cb',None)
        if not self._cb and len(args) > 0 and hasattr(args[0],'__call__'):
            self._cb = args[0]
        if not self._cb:
            raise Exception('Callback needed')

        self._methods = kwargs.get('methods',[])
        if not self._methods and len(args) > 1 and isinstance(args[1],list):
            self._methods = args[1]
        self._methods = [ m.upper() for m in self._methods if isinstance(m,str) and m.upper() in ['GET','POST'] ]
        if not self._methods:
            raise Exception('Method needed')

        self._default_http_code = kwargs.get('default_http_code',None)
        if not self._default_http_code and len(args) > 2 and isinstance(args[2],int):
            self._default_http_code = args[2]
        if not self._default_http_code:
            raise Exception('Default http code needed')

    def post(self):
        if 'POST' not in self._methods:
            return ''
        if self._cb:
            log.debug('[POST]')
            return make_response(self._cb(),self._default_http_code)

    def get(self):
        if 'GET' not in self._methods:
            return ''
        if self._cb:
            return make_response(self._cb(),self._default_http_code)

class HealthRequest(ListenerRequest):
    def get(self):
        return make_response(str(self._cb()),200)

class ServerManager:
    PORT=LISTENERPORT
    HOST=LISTENERHOST

    def __init__(self,*args,**kwargs):
        self._app = None
        self._cb = []
        self._exitting = False
        self._thread = threading.Thread(name='ServerManager', target=self.run)
        self._thread.setDaemon(True)

    def start(self):
        try:
            if not self._thread.is_alive():
                self.addCallback(
                    ListenerRequest,
                    '/analytics/notify',
                    process
                )
                self.addCallback(
                    HealthRequest,
                    '/analytics/health',
                    health
                )
                self._thread.start()
        except Exception as e:
            log.error('ServerManager error, {}'.format(e))

    def stop(self):
        log.info('Exitting server')
        self._exitting = True

    def addCallback(self,methodviewclass,endpoint,method,httpmethodlist=['POST'],httpcode=200):
        log.debug("New endpoint {} '{}' with {}".format(httpmethodlist,endpoint,methodviewclass.__name__))
        self._cb.append((methodviewclass,endpoint,method,httpmethodlist,httpcode))

    def run(self):
        while not self._exitting:
            time.sleep(1)
            self._app = Flask(__name__)
            # _log = logging.getLogger('werkzeug')
            # if _LOG_LEVEL == 0:
            #     _log.addHandler(logging.NullHandler)
            #     _log.disabled = True
            # else:
            #     _log.setLevel(_LOG_LEVEL)
            log.debug('New application')
            for methodviewclass, endpoint, method, httpmethodlist, httpcode in self._cb:
                self._app.add_url_rule(
                    endpoint, 
                    endpoint, 
                    methodviewclass.as_view(endpoint,method,httpmethodlist,httpcode) 
                )
                log.debug("Registered {} '{}' with {}".format(httpmethodlist,endpoint,methodviewclass.__name__))
            try:
                log.info('Starting app')
                self._app.run(host=self.HOST,port=self.PORT)
                log.info('App ended')    
            except Exception as e:
                log.error('App fail to start, {}'.format(e))

    def healthcheck(self):
        return self._thread.is_alive()

def exitting(signum=None, frame=None):
    global running, queue, server
    log.info('Exitting by signal {}, stopping all threads'.format(signum))
    queue.stop()
    server.stop()
    running=False

def health():
    global queue
    if queue:
        return queue.healthcheck()

def process():
    global queue
    if not queue:
        raise Exception('No queue')
    data = request.form.get('stats',None)
    if not data:
        return ''
    try:
        out, data = AnalyticsReceiver.makeMessage(data)
        if out == 'OK' and data:
            queue.schedule_next_message(message=data)
        return out
    except Exception as e:
        log.error('Error processing data, {}'.format(e))

if __name__ == "__main__":
    log.info('Starting Listener')
    signal.signal(signal.SIGTERM,exitting)
    signal.signal(signal.SIGQUIT,exitting)
    running = False
    queue = None
    server = None
    try:
        url = 'amqp://{}:{}@{}:{}/{}?connection_attempts=3&heartbeat=3600'.format(
            RABBITUSER,
            RABBITPASSWORD,
            RABBITHOST,
            RABBITPORT,
            RABBITVHOST.replace('/','%2F')
        )
        queue = QueueManager()
        queue.start(url)
        log.info('QueueManager started')
    except Exception as e:
        log.error('Error QueueManager initialization, {}'.format(e))
        sys.exit(1)
    try:
        server = ServerManager()
        server.start()
        log.info('ServerManager started')
    except Exception as e:
        log.error('Error ServerManager initialization, {}'.format(e))
        sys.exit(1)
    running=True
    try:
        i=30
        while running:
            if not i:
                log.info('Listener active: Alive: Server/Queue {}/{}'.format(
                    server.healthcheck() if server else False,
                    queue.healthcheck() if queue else False
                ))
                i=10
            time.sleep(1)
            i-=1
    except Exception as e:
        log.error("End listener by '{}', exitting from main thread now".format(e))
        exitting()
    log.info("End listener application")
    sys.exit(0)