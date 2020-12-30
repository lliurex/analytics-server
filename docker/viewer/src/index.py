import threading
import mysql.connector
import time
import os
import logging
import logging.config
import signal
import json
import string
from datetime import datetime as dt
from datetime import timedelta as td

from flask import Flask,Response,make_response,request,jsonify,json,render_template
from flask.views import MethodView

LOG_LEVEL       = os.environ.get('LOG_LEVEL','NOTSET')
LISTENERHOST    = '0.0.0.0'
LISTENERPORT    = os.environ.get('LISTENER_PORT',80)
MYSQL_DATABASE  = os.environ.get('MYSQL_DATABASE','analytics')
MYSQL_USER      = os.environ.get('MYSQL_USER','analytics')
MYSQL_PASSWORD  = os.environ.get('MYSQL_PASSWORD','analytics')
MYSQL_HOST      = os.environ.get('MYSQL_HOST','db')
PREFIX_URL      = os.environ.get('PREFIX_URL','analytics')
STATIC_PATH     = os.environ.get('STATIC_PATH','static')

DISTROS = ['15','16','19','21']
FLAVOURS = ['desktop','server','client']

def runningInDocker():
    with open('/proc/self/cgroup', 'r') as procfile:
        for line in procfile:
            fields = line.strip().split('/')
            if fields[1] == 'docker':
                return True

standalone = not runningInDocker()
if standalone:
    LOG_LEVEL = 'DEBUG'
    LISTENERPORT    = 8080
    MYSQL_HOST = 'localhost'

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

REQUEST_LOCK = threading.Lock()

class View(MethodView):
    def __init__(self,*args,**kwargs):
        self.template = None
        self._json = False
        self.params = {
            'csslib': [],
            'jslib' : [],
            'jscmd' : [],
        }

    def post(self,*args,**kwargs):
        if self._json:
            result = kwargs.get('dbresult',None)
            if not result:
                raise Exception('Empty result from database')
            return make_response(jsonify(result))
        else:
            if self.template:
                return render_template(self.template,**self.params)
            else:
                return make_response('[POST] {}\n'.format(self.__class__.__name__))

    def get(self,*args,**kwargs):
        if self._json:
            result = kwargs.get('dbresult',None)
            if not result:
                raise Exception('Empty result from database')
            return jsonify(result)
        else:
            if self.template:
                return render_template(self.template,**self.params)
            else:
                return make_response('[GET] {}\n'.format(self.__class__.__name__))

    def head(self):
        return make_response()

class IndexView(View):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.template = 'index.tpl'
        self.params['csslib'].append('/analytics/static/graph')
        self.params['navigation'] = [
            { 'caption': 'Simple Statistics', 'href': 'ShowStats' },
            { 'caption': 'Extended Statistics', 'href': 'ShowExtendedStats' },
            { 'caption': 'Lliurex Statistics', 'href': 'ShowLliurexStats' },
            { 'caption': 'Whitelist Config', 'href': 'ConfigureWhitelist' },
#            { 'caption': 'System Status', 'href': 'ShowSystemStats' }
        ]

class StatsView(IndexView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.params['csslib'].insert(0,'/analytics/static/ui/jquery-ui')
        self.params['jslib'].extend(['https://www.gstatic.com/charts/loader','/analytics/static/jquery.min','/analytics/static/graph_min','/analytics/static/ui/jquery-ui','/analytics/static/query_min'])
        self.params['jscmd'].append('google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(doChart);')
        self.params['jscmd'].append('$(document).ready(make_query_box);')

class JsonView(View):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        global REQUEST_LOCK
        self._mtx = REQUEST_LOCK
        self._json = True
        if len(args) > 0:
            self._db = args[0]
        else:
            self._db = None
        self.TIMES = 0
        self._dates = self.init_dates()
        self._distros = self.init_distros()
    
    def execute(self,*args,**kwargs):
        stime = time.time()
        ret = self._db.execute(*args,**kwargs)
        self.TIMES += (time.time()-stime)
        return ret

    def init_dates(self,daterange={}):
        f="%Y-%m-%d"
        dates = { 'today': dt.today().strftime(f) }
        tmp = dt.today()
        dates.setdefault('first_current',"{}-{}-01".format(tmp.year,tmp.month))
        tmp = dt.strptime(dates.get('first_current'),f)
        dates.setdefault('last_old',(tmp-td(days=1)).strftime(f))
        tmp = dt.strptime(dates.get('last_old'),f)
        dates.setdefault('first_old',"{}-{}-01".format(tmp.year,tmp.month))
        tmp = dt.strptime(dates.get('first_old'),f)
        dates.setdefault('last_very_old',(tmp-td(days=1)).strftime(f))
        tmp = dt.strptime(dates.get('last_very_old'),f)
        dates.setdefault('first_very_old',"{}-{}-01".format(tmp.year,tmp.month))
        dates.setdefault('date_current',"(date between '{}' and '{}')".format(dates.get('first_current'),dates.get('today')))
        dates.setdefault('date_old',"(date between '{}' and '{}')".format(dates.get('first_old'),dates.get('last_old')))
        dates.setdefault('date_very_old',"(date between '{}' and '{}')".format(dates.get('first_very_old'),dates.get('last_very_old')))
        dates.setdefault('date_range_last_three_months',"(date between '{}' and '{}')".format(dates.get('first_very_old'),dates.get('today')))
        if daterange:
            y = int(daterange.get('year',None))
            m = int(daterange.get('month',None))
            w = int(daterange.get('window',None))
            today = dt.today()
            if y < today.year-1 or y > today.year:
                return dates
            if m < 1 or m > 12:
                return dates
            if w < 1 or w > 12:
                return dates
            dates.setdefault('init_range',"{}-{}-01".format(y,m))
            tmp = dt.strptime(dates.get('init_range',None),f)
            for i in range(w):
                m += 1
                if m > 12:
                    y += 1
                    m = 1
            d=1
            if y == today.year and m == today.month:
                d = today.day
            tmp2 = dt(year=y,month=m,day=d)
            if tmp2 > today:
                tmp2 = today
            dates.setdefault('end_range',(tmp2).strftime(f))
            dates.setdefault('custom_range',"(date between '{}' and '{}')".format(dates.get('init_range'),dates.get('end_range')))
        return dates

    def init_distros(self):
        dl = []
        for distro in DISTROS:
            d = { 'name' : distro , 'like': distro, 'flavour': [] }
            for flavour in FLAVOURS:
                f = { 'name': flavour, 'like': flavour }
                d['flavour'].append(f)
            dl.append(d)
        dl.append({'name': 'other', 'like': '', 'flavour': [{ 'name': 'other', 'like': 'other' }]})                
        return dl

    def to_python_object(self,*args):
        if len(args) != 1:
            args = list(args)
        else:
            args = args[0]
        if isinstance(args,list):
            if len(args) == 1:
                args = self.to_python_object(args[0])
            else:
                for i in range(len(args)):
                    args[i] = self.to_python_object(args[i])
        elif isinstance(args,dict):
            for k,v in args.items():
                args[k] = self.to_python_object(v)
        else:
            if not isinstance(args,(str,int)):
                args = int(args)
        return args

    def get(self,*args,**kwargs):
        return super().get(*args,**kwargs)
    def post(self,*args,**kwargs):
        return super().post(*args,**kwargs)

class HealthView(JsonView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    def get(self):
        try:
            req = request
            ret = self.healthcheck()
        except Exception as e:
            ret = {'Error': str(e) }
        kw = {'dbresult': ret}
        return super().get(**kw)

    def healthcheck(self):
        try:
            names = self._db.execute('Select name from Releases')
            names = [x.get('name') for x in names]
            for x in ['15', '16', '19', '21', 'other']:
                if not x in names:
                    return False
            return True
        except Exception as e:
            return {'Error': str(e) }

class StatsJsonView(JsonView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    def get(self, **kwargs):
        param = self.process_window_params(request)
        if kwargs:
            kw = kwargs
        else:
            if self._mtx.locked():
                log.info('Discarding request while running another')
                return make_response('',429)
            self._mtx.acquire()
            kw = {'dbresult': self.to_python_object(self.get_historic_data('',param))}
            self._mtx.release()
        return super().get(**kw)

    def process_window_params(self,req):
        if not req:
            return {}
        init = req.args.get('init',None)
        window = req.args.get('window',None)
        if not init or not window:
            return {}
        try:
            init_year = int(init[:4])
            init_month = int(init[4:])
            window = int(window)
        except:
            return {}
        if not init_year or not init_month or not window:
            return {}
        if window < 1 or window > 12:
            return {}
        today = dt.today()
        if init_year not in [today.year,today.year-1]:
            return {}
        if init_month < 1 or init_month > 12:
            return {}
        init_day = 1
        selected = dt(year=init_year,month=init_month,day=init_day)
        if selected > today:
            selected = today
            window = 1
        for i in range(window):
            init_month += 1
            if init_month > 12:
                init_month = 1
                init_year += 1
        if init_year == today.year and init_month == today.month:
            init_day = today.day
        until = dt(year=init_year,month=init_month,day=init_day)
        if until > today:
            until = today
        return {'year':selected.year,'month':selected.month,'window':window}

    '''
    def get_historic_data2(self,typechart='',param={}):
        obj = {}
        ages = ['current','old','very_old']
        data = {}
        for age in ages:
            sql = "SELECT * from v_month_{}".format(age)
            data.setdefault(age,self.execute(sql))

        for age in ages:
            pos = ages.index(age)
            dage = data.get(age)
            for d in dage:
                dname = d.get('Releases_name')
                sname = d.get('Flavours_name')
                app = d.get('string')
                count = d.get('count')
                obj.setdefault(dname,{})
                obj[dname].setdefault(sname,[[{},{"nclients":0}],[{},{"nclients":0}],[{},{"nclients":0}]])
                obj[dname][sname][pos][0].setdefault(d.get('string'),d.get('count'))
        
        obj.setdefault('debug_query_time','{}'.format(self.TIMES))
        for k in ['init_range','end_range']:
            if k in self._dates:
                obj.setdefault('debug_{}'.format(k),'{}'.format(self._dates.get(k)))
        return obj
    '''

    def get_historic_data(self,typechart='',param={}):
        obj = {}
        ages = ['current','old','very_old']
        for distro in self._distros:
            dname = distro.get('name')
            dlike = distro.get('like')
            obj.setdefault(dname,{})
            for flavour in distro.get('flavour'):
                sname = flavour.get('name')
                slike = flavour.get('like')
                obj[dname].setdefault(sname,[])
                for age in ages:
                    obj[dname][sname].append(self.get_chart(dlike,slike,age,typechart,param))
                    if param:
                        break
        obj.setdefault('debug_query_time','{}'.format(self.TIMES))
        if param:
            self._dates = self.init_dates(param)
        for k in ['init_range','end_range']:
            if k in self._dates:
                obj.setdefault('debug_{}'.format(k),'{}'.format(self._dates.get(k)))
        return obj

    def get_chart(self,version=None,flavour=None,age='current',typechart='',param={}):
        limit = ''
        sql_limit = 1000
        additional_condition = "and string in ( select `name` from `PackagesWhitelist` where status = '1' )"
        if not typechart:
            limit = "limit 10"
            sql_limit = 10
            additional_condition = ''
        if version:
            version = " and Releases_name = '{}' ".format(version)
        if flavour:
            flavour = " and Flavours_name = '{}' ".format(flavour)
        order = " order by count desc {}".format(limit)
        group = " group by app "
        where = ""
        if not param:
            where = "{} {} {} ".format(
                self._dates.get('date_'+age,None),
                version,
                flavour
            )
        else:
            dates = self.init_dates(param)
            where = "{} {} {} ".format(
                dates.get('custom_range',None),
                version,
                flavour
            )
        where_clients = where
        force_index = True
        index = ''
        if force_index:
            index = 'use index(get_top_apps)'

        sql = "SELECT string as app, sum(count) as count from RecvPackages {} where {} {} {} {}".format(
            index,
            where,
            additional_condition,
            group,
            order
        )
       
        # Possible use alternative view: (from {age}_{distro}_{flavour}) (not better, this is a query explained as "simple")

        sql_clients = "SELECT count(distinct Client_uid) as count from Client_Versions where {} {}".format(
            where_clients,
            order
        )
        return [self.get_results_from_sql(sql,sql_limit),self.get_clients_from_sql(sql_clients)]

    def get_clients_from_sql(self,sql=""):
        if sql:
            try:
                result = self.execute(sql)
                if len(result) == 1:
                    result = result[0]
                else:
                    raise Exception('Expecting single result from query')
                return {'nclients': result.get('count')}
            except Exception as e:
                return {'nclients': '{}'.format(e)}
        else:
            return {'nclients':'No sql provided'}

    def get_results_from_sql(self,sql="",limit=0):
        if sql:
            result = []
            try:
                result_sql = self.execute(sql)
                for r in result_sql:
                    result.append([r.get('app',None),r.get('count',None)])
                    if len(result) > limit:
                        break
                return result
            except Exception as e:
                return "{}".format(e) 
        else:
            return "{}".format('No sql provided')

class StatsExtendedView(IndexView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.template = 'extended.tpl'
        self.params['csslib'].insert(0,'/analytics/static/ui/jquery-ui')
        self.params['jslib'].extend(['https://www.gstatic.com/charts/loader','/analytics/static/jquery.min','/analytics/static/graph_min','/analytics/static/ui/jquery-ui','/analytics/static/query_min'])
        self.params['jscmd'].append('google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(doExtendedChart);')
        self.params['jscmd'].append('$(document).ready(function(){function send_query(){window.location.href=window.location.pathname+"?app="+$("#query_box>input").val()};$("#query_box>input").on("keyup",function(e){if (e.keyCode == 13) {send_query()}});$("#query_box>button").click(send_query)});')

class StatsJsonExtendedView(JsonView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def get(self):
        if self._mtx.locked():
            log.info('Discarding request while running another')
            return make_response('',429)
        self._mtx.acquire()
        app = request.args.get('app',None)
        kw = {'dbresult': self.to_python_object(self.get_extended_data(app))}
        self._mtx.release()
        return super().get(**kw)

    def get_extended_data(self,app=''):
        sql = "SELECT * from resume order by year desc, month desc"
        ret = self.execute(sql)
        num_updates_month = [0]*12
        machines_month = [0]*12
        change_releases = [0]*12
        change_flavour = [0]*12
        if not ret:
            raise Exception('Empty result from sql')
        i = 0
        for x in ret:
            total_hosts = x.get('total_hosts',0) if x.get('total_hosts',0) else 0
            machines_month[i] = total_hosts
            a = x.get('a',0) if x.get('a',0) else 0
            b = x.get('b',0) if x.get('b',0) else 0
            change_releases[i] = a + b
            c = x.get('c',0) if x.get('c',0) else 0
            d = x.get('d',0) if x.get('d',0) else 0
            change_flavour[i] = c + d
            e = x.get('e',0) if x.get('e',0) else 0
            num_updates_month[i] = e
            i+=1
            if i == 12:
                break
        
        sql = "SELECT * from v_nhosts"
        res = self.pack(sql=sql,value='total_hosts')
        clients_month = list()
        for key_date,value in res.items():
            clients_month.append(value)
        
        sql = "SELECT * from v_architectures"
        res = self.pack(sql=sql,value='total',keys=[['year','month'],'rel','fla','arch'])
        clients_arch = list()
        for key_date,value in res.items():
            clients_arch.append(value)
        
        sql = "SELECT * FROM v_mem_resume"
        res_sql = self.execute(sql)
        clients_mem = list()
        res = self.pack(data=res_sql,value=['null','2g','4g','8g'])
        for key_date,value in res.items():
            clients_mem.append(value)

        sql = "SELECT * FROM v_cpu_resume"
        res_sql = self.execute(sql)
        clients_cpu = list()
        res = self.pack(data=res_sql,value=['null','mono','dual','more'])
        for key_date,value in res.items():
            clients_cpu.append(value)

        sql = "SELECT * from v_ltsp_types"
        res = self.pack(sql=sql,value='total',keys=[['year','month'],'type'])
        count_ltsp = list()
        for key_type,value in res.items():
            count_ltsp.append(value)

        sql = "SELECT * from v_ltsp_modes"
        res = self.pack(sql=sql,value='total',keys=[['year','month'],'mode'])
        count_mode = list()
        for key_mode,value in res.items():
            count_mode.append(value)
        
        app_detail = None
        if app:
            app_detail = self.get_app_detail(app)

        stats = {
            'clients': {
                'clients_per_month': clients_month,
                'machines_per_month': machines_month,
                'freq_updates_per_month': num_updates_month,
                'change_releases': change_releases,
                'change_flavours': change_flavour,
                'architectures': clients_arch,
                'mem': clients_mem,
                'cpu': clients_cpu,
                'count_ltsp': count_ltsp,
                'count_mode': count_mode
            },
            'debug_query_time': '{}'.format(self.TIMES)
        }
        if app_detail:
            for k,v in app_detail.items():
                stats[k]=v
        return stats

    def get_app_detail(self,app=None):
        app = self.validate_input(app)
        if not app:
            return None
        sql = "SELECT `year`,`month`,`rel`,`fla`,`string`,IFNULL(`count`,0) AS count FROM `compat_rf` JOIN (SELECT DISTINCT `string` FROM `RecvPackages` WHERE `string` LIKE '{}%' LIMIT 10)compat_rfapp LEFT JOIN (SELECT YEAR(`date`) AS year, MONTH(`date`) AS month,`string`,`Releases_name` AS rel,`Flavours_name` AS fla,SUM(`count`) AS count FROM `RecvPackages` WHERE `string` LIKE '{}%' AND `date` >= DATE_SUB(NOW(),INTERVAL 1 YEAR) GROUP BY `year`,`month`,`string`,`Releases_name`,`Flavours_name`)a USING(`year`,`month`,`rel`,`fla`,`string`) ORDER BY compat_rfapp.string,year DESC, month DESC".format(app,app)
        res = self.pack(sql=sql,value='count',keys=['string',['year','month'],'rel','fla'])
        out = {}
        for app_string,values in res.items():
            app_use = []
            for date,reldata in values.items():
                app_use.append(reldata)
            out.setdefault('apps',[])
            out['apps'].append({'app':app_string,'app_use':app_use})
        return out

    def validate_input(self,s):
        if not isinstance(s,str):
            return None
        if len(s) > 20:
            return None
        valid_chars = list(string.ascii_letters + string.digits + '-_.')
        for x in s:
            if x not in valid_chars:
                return None
        return s

    def pack(self,sql=None,data=None,value=None,keys=[['year','month'],'rel','fla']):
        if not sql and not data:
            raise Exception()
        if sql:
            res = self.execute(sql)
        elif data:
            res = data
        d = {}
        for x in res:
            tmp = d
            for key in keys:
                if isinstance(key,list):
                    keyval = '_'.join(map(str,map(x.get,key)))
                else:
                    keyval = x.get(key)
                keyval = keyval.lower()
                if key != keys[-1]:
                    tmp.setdefault(keyval,{})
                    tmp = tmp[keyval]
                else:
                    if isinstance(value,list):
                        tmpdict = {}
                        for k in value:
                            tmpdict.setdefault(k,x.get(k))
                        tmp.setdefault(x.get(keys[-1]),tmpdict)
                    else:
                        tmp.setdefault(x.get(keys[-1]),x.get(value))
        return d

class StatsLliurexView(IndexView):
    def __init__(self,*args,**kwargs):
        super().__init__()
        self.params['csslib'].extend(['/analytics/static/ui/jquery-ui','/analytics/static/graph'])
        self.params['jslib'].extend(['https://www.gstatic.com/charts/loader','/analytics/static/jquery.min','/analytics/static/graph_min','/analytics/static/ui/jquery-ui','/analytics/static/query_min'])
        self.params['jscmd'].append('google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(function(){doChart("whitelist")});')
        self.params['jscmd'].append('$(document).ready(make_query_box);')

class StatsJsonLliurexView(StatsJsonView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    
    def get(self):
        if self._mtx.locked():
            log.info('Discarding request while running another')
            return make_response('',429)
        self._mtx.acquire()
        param = self.process_window_params(request)
        kw = {'dbresult': self.to_python_object(self.get_historic_data('whitelist',param))}
        self._mtx.release()
        return super().get(**kw)

class WhitelistConfigureView(IndexView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.template = 'whitelist.tpl'
        self.params['csslib'].extend(['/analytics/static/whitelist','/analytics/static/graph'])
        self.params['jslib'].extend(['/analytics/static/jquery.min','/analytics/static/whitelist_min'])
        self.params['jscmd'].append('$(document).ready(start);')
        
        self.params['navigation'] = [
            { 'caption': 'Simple Statistics', 'href': 'ShowStats' },
            { 'caption': 'Extended Statistics', 'href': 'ShowExtendedStats' },
            { 'caption': 'Lliurex Statistics', 'href': 'ShowLliurexStats' },
            { 'caption': 'Whitelist Config', 'href': 'ConfigureWhitelist' },
            # { 'caption': 'System Status', 'href': 'ShowSystemStats' }
        ]

class WhitelistItemsView(JsonView):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.valid_input = string.ascii_letters + string.digits + '_-()+.[]{}'

    def get(self):
        req = request
        if self._mtx.locked():
            log.info('Discarding request while running another')
            return make_response('',429)
        self._mtx.acquire()
        kw = {'dbresult': self.to_python_object(self.get_whitelist_form())}
        self._mtx.release()
        return super().get(**kw)

    def sanitize(self,*args):
        r = None
        for x in args:
            if isinstance(x,str):
                return ''.join([i for i in x if i in self.valid_input])
            elif isinstance(x,tuple):
                r = tuple()
                for i in x:
                    r += ( self.sanitize(i), )
            elif isinstance(x,list):
                r = []
                for i in x:
                    r += [self.sanitize(i)]
            else:
                pass
        return r

    def post(self):
        status = None
        out = None
        into = None
        
        try:
            status = json.loads(request.form.get('status'))
            out = self.sanitize(status.get('out'))
            into = self.sanitize(status.get('into'))
        except:
            status = None
        if not status or not isinstance(out,list) or not isinstance(into,list):
            return 'NOK'
        sql1 = 'TRUNCATE PackagesWhitelist;'
        sql2 = 'INSERT INTO `PackagesWhitelist` (`name`,`status`) VALUES {} ON DUPLICATE KEY UPDATE status=VALUES(status);'
        where = '({})'.format(','.join(map(lambda x: "'{}'".format(x),out)))
        sql3 = 'INSERT INTO `RecvPackages_purged` SELECT * FROM `RecvPackages` WHERE `string` in {}'.format(where) 
        sql4 = 'DELETE FROM `RecvPackages` WHERE `string` in {}'.format(where)
        values = ['{}'.format((x,0)) for x in out]
        values += ['{}'.format((x,1)) for x in into]
        try:
            self.execute(sql1)
            values = ','.join(values)
            sql2 = sql2.format(values)
            self.execute(sql2)
            self.execute(sql3)
            self.execute(sql4)
            self.execute('commit;')
        except:
            self.execute('rollback;')
            return 'NOK'
        return 'OK'

    def get_whitelist_form(self):
        sql_packages = "SELECT distinct `string` from `RecvPackages` order by `string`"
        sql_whitelist = "SELECT `name`,`status` from `PackagesWhitelist`"
        packages = self.execute(sql_packages)
        packages = [ o.get('string') for o in packages ]
        res = self.execute(sql_whitelist)
        whitelist = {'in':[],'out':[],'unk':[]}
        classified = {}
        for o in res:
            status = o.get('status')
            name = o.get('name')
            if status == 0:
                whitelist['out'].append(name)
                classified.setdefault(name,None)
            elif status == 1:
                whitelist['in'].append(name)
                classified.setdefault(name,None)
        for package in packages:
            if package not in classified:
                whitelist['unk'].append(package)
        return whitelist

class WhitelistView(IndexView):
    pass

class SystemView(View):
    pass

class SystemJsonView(JsonView,SystemView):
    pass

class ServerManager:
    PORT=LISTENERPORT
    HOST=LISTENERHOST

    def __init__(self,*args,**kwargs):
        self._app = None
        self._db = None
        self._thread = threading.Thread(name='ServerManager', target=self.run)
        self._thread.setDaemon(True)
        self._cb = [
            (IndexView,'/analytics/Index',['GET']),
            (StatsView,'/analytics/ShowStats',['GET']),
            (StatsJsonView,'/analytics/GetStats',['GET']),
            (StatsExtendedView,'/analytics/ShowExtendedStats',['GET']),
            (StatsJsonExtendedView,'/analytics/GetExtendedStats',['GET']),
            (StatsLliurexView,'/analytics/ShowLliurexStats',['GET']),
            (StatsJsonLliurexView,'/analytics/GetLliurexStats',['GET']),
            (WhitelistConfigureView,'/analytics/ConfigureWhitelist',['GET']),
            (WhitelistItemsView,'/analytics/GetWhitelistItems',['GET']),
            (WhitelistItemsView,'/analytics/PutWhitelist',['POST']),
            (WhitelistView,'/analytics/getlist',['GET']),
            (SystemView,'/analytics/ShowSystemStats',['GET']),
            (SystemJsonView,'/analytics/SystemStats',['GET']),
            (HealthView,'/analytics/health',['GET'])
        ]
        self._exitting = False

    def start(self):
        self._thread.start()
        log.info('ServerManager started')

    def stop(self):
        log.info('Exitting server')
        self._exitting = True

    def run(self):
        global STATIC_PATH, PREFIX_URL
        self._db = AnalyticsDatabase(
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            host=MYSQL_HOST,
            database=MYSQL_DATABASE
        )
        self._db.connect()
        while not self._exitting:
            if not STATIC_PATH:
                STATIC_PATH = ''
            else:
                if STATIC_PATH[0] != '/':
                    STATIC_PATH = '/' + STATIC_PATH
            if not PREFIX_URL:
                PREFIX_URL = ''
            else:
                if PREFIX_URL[0] != '/':
                    PREFIX_URL = '/' + PREFIX_URL
            self._app = Flask(__name__,static_url_path='{}{}'.format(PREFIX_URL,STATIC_PATH))
            log.debug('New application')
            for methodviewclass, endpoint, httpmethodlist in self._cb:
                rule = endpoint
                endpoint = endpoint
                view_func = methodviewclass.as_view(endpoint,self._db)
                provide_automatic_options = False
                options = { 'methods' : tuple(httpmethodlist) }
                self._app.add_url_rule(
                    rule,
                    endpoint, 
                    view_func,
                    provide_automatic_options,
                    **options
                )
                log.debug("Registered {} '{}' with {}".format(httpmethodlist,endpoint,methodviewclass.__name__))
            log.debug('{}'.format(self._app.url_map))
            try:
                log.info('Starting app')
                self._app.run(host=self.HOST,port=self.PORT)
                log.info('App ended')    
            except Exception as e:
                log.error('App fail to start, {}'.format(e))
            time.sleep(1)

class AnalyticsDatabase(object):
    def __init__(self, user=None, password=None, host=None, database=None ):
        self._user = user
        self._password = password
        self._host = host
        self._database = database
        self._connection = None
        self._cursor = None
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
        if e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            log.error('MySQL connector error, wrong username/password')
        elif e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            log.error('MySQL connector error, wrong database')
        elif e.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
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
                cur = self._connection.cursor(dictionary=True)
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
        res = None
        while retry and not done:
            try:
                self._mutex.acquire()
                stime = time.time()
                self._cursor.execute(statement)
                dur = time.time()-stime
                log.info('Execution into db succeded, {}'.format(dur))
                if dur > 0.1:
                    log.info('Long SQL:>\n{}\n\n'.format(statement))
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
        if self._cursor.with_rows:
            return self._cursor.fetchall()
        else:
            return None

def exitting(signum=None, frame=None):
    global running, server
    log.info('Exitting')
    server.stop()
    running=False

if __name__ == "__main__":
    log.info('Starting Listener')
    signal.signal(signal.SIGTERM,exitting)
    signal.signal(signal.SIGQUIT,exitting)
    running=True

    server = ServerManager()
    server.start()
    
    db = AnalyticsDatabase(
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        database=MYSQL_DATABASE
    )
    health = HealthView(db)

    try:
        i = 60
        while running:
            if not i:
                i = 20
                log.debug('Listener active: health: {}'.format(health.healthcheck()))
            i -= 1
            time.sleep(1)
    except Exception as e:
        exitting()
        log.debug('End listener ({})'.format(e))
