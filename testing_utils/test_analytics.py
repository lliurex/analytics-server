#!/usr/bin/python
import _mysql
import urllib2
import requests
import sys
from collections import deque
import random
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Lock 
import json
import time
import operator
import threading
import signal
from datetime import datetime
from dateutil.relativedelta import relativedelta

IP=''
HOST='http://aplicaciones.lliurex.net/analytics/notify'
HEADERS={'user-agent':'lliurex-statistics-agent'}
TIMEOUT=30              # TIMEOUT SENDING REQUESTS

RELEASES=['16','15']
MAX_RELNUMBER=5         # MAX RELEASE VARIATION
REAL_FLAVOURS=True      # TRUE FLAVOURS (release 15)
DATE_ROUNDS=1           # DIFERENTS MONTHS SENDED
NCLIENTS=20           # NUMBER DIFFERENT CLIENTS
MAX_THREADS=5           # PARALLEL CLIENTS SENDING DATA (> 5 == no effect)
CACHE_CONNECTIONS=1     # python requests cache hosts
NAPPS=5000                # MAX NUMBER DIFFERENT APPS
CLIENT_MAX_APPS=100      # MAX NUMBER APPS SENDING
CLIENT_UPDATE_FREQ=15    # PERCENT OF CLIENTS THAT UPDATE INTRA ROUND
DO_UPGRADES = True
UPGRADE_PROB=15          # PERCENT OF CLIENTS THAT UPGRADES WHEN UPDATE
LOOPS=5                # LOOPS INTRA DATE LOOP
SLEEP_THREAD_TIME=0     # SLEEP THREAD AFTER SENDING
STATS_ON=1              # req/s stats

PRINT_UPDATES=True
USE_PLATFORM_DATA=True
USE_LTSP_DATA=True
USE_LTSP_WITH_OLD_CLIENTS=False
MAX_RANDOM_CLIENTS=50000
DEBUG=0
SHOW_BY_APP=True
PAUSE_SHOW_STATS=False
PAUSE_WITH_DATE_ROUNDS=False
# STAT COUNTERS
NPET=0
SUCCESS=0
FAILED=0
REDO=0
UPDATED_TOTAL=0
UPDATED=0
RANDOM=True     # Random generation releases, flavours, macs

exit_threads=0
FLAVOURS={}
if REAL_FLAVOURS:
    FLAVOURS['16']=[
                {'name':'edu,server','real':'server'},
                {'name':'server','real':'server'},
                {'name':'edu','real':'other'},
                {'name':'edu,music','real':'other'},
                {'name':'client','real':'client'},
                {'name':'client','real':'client'},
                {'name':'desktop,edu','real':'desktop'},
                {'name':'client,edu','real':'client'},
                {'name':'client,edu,infantil','real':'client'},
                {'name':'desktop,edu','real':'desktop'},
                {'name':'desktop,edu,infantil','real':'desktop'},
                {'name':'desktop,edu,infantil,music','real':'desktop'},
                {'name':'desktop,edu,music','real':'desktop'},
                {'name':'server','real':'server'},
                {'name':'pime','real':'other'},
                {'name':'server','real':'server'}]
    FLAVOURS['15']=[
                {'name':'cdd,class,client,desktop,edu,lliurex,ltsp,net,network-client-promo','real':'client'},
                {'name':'cdd,lliurex','real':'other'},
                {'name':'cdd,lliurex,network-client-promo','real':'client'},
                {'name':'cdd,desktop,lliurex','real':'desktop'},
                {'name':'cdd,desktop,lliurex,music','real':'desktop'},
                {'name':'cdd,desktop,edu,lite-extended,lliurex','real':'desktop'},
                {'name':'cdd,desktop,edu,infantil,lliurex','real':'desktop'},
                {'name':'cdd,desktop,gva,lliurex','real':'desktop'},
                {'name':'cdd,desktop,edu,enterprise,infantil,lliurex','real':'desktop'},
                {'name':'cdd,class,desktop,edu,lliurex,ltsp,server','real':'server'},
                {'name':'server','real':'server'},
                {'name':'client','real':'client'},
                {'name':'desktop','real':'desktop'},
                {'name':'cdd,class,desktop,edu,live,lliurex,ltsp,server','real':'server'},
                {'name':'server,cdd','real':'server'},
                {'name':'client,cdd','real':'client'}]
else:
    FLAVOURS['16']=[
                {'name':'server','real':'server'},
                {'name':'client','real':'client'},
                {'name':'desktop','real':'desktop'},
                {'name':'other','real':'other'}]
    FLAVOURS['15']=[
                {'name':'server','real':'server'},
                {'name':'client','real':'client'},
                {'name':'desktop','real':'desktop'},
                {'name':'other','real':'other'}]


ARCHS=['x86_64','i386']
LTSP_MODES=['THIN','SEMI']
SLEEP_FAIL_SENDING=1

class DB():
    def __init__(self):
        self.conn=None

    def init_db(self):
        try:
            self.conn = _mysql.connect(IP,USER,PASS,DBNAME)
            print "Connected succesfully"

        except _mysql.Error, e:
            print "Error {}: {}".format(e.args[0],e.args[1])
            sys.exit(1)

    def close_db(self):
        if self.conn:
            self.conn.close()
            print "Closed connection"

if RANDOM and NCLIENTS <= MAX_RANDOM_CLIENTS:
    MACS_USED=[]
else:
    MAC_LIST=deque()
    a=0
    b=0
    c=0
    for i in range(NCLIENTS):
        c+=1
        mac = "02:00:00:%02x:%02x:%02x" % (a,b,c)
        if c == 255:
            c=0
            b+=1
            sys.stderr.write('{}Generating consecutive mac: {:07d}'.format('\r'*100,i+1))
        if b == 255:
            b=0
            c+=1
        MAC_LIST.append(mac)
    sys.stderr.write('{}Generating consecutive mac: {:07d}\n'.format('\r'*100,NCLIENTS))

class CLIENT():
    def __init__(self):
        self.mac=self.gen_mac()
        self.num=None
        self.year=None
        self.month=None
        self.day=None
        if RANDOM:
            self.release=RELEASES[random.randint(0,4)%2] # more probabilities for the first listed release
        else:
            self.release=RELEASES[0]
        self.release_number=self.gen_rel_number()
        if RANDOM:
            fla=FLAVOURS[self.release][random.randint(0,len(FLAVOURS[self.release])-1)]
        else:
            fla=FLAVOURS[self.release][0]
        self.flavour=fla['name']
        self.real_flavour=fla['real']
        self.updates=0
        self.inc_date=0
        self.ltsp=False
        self.mode=False
        if USE_PLATFORM_DATA:
            pdata = self.gen_platform_data()
            for att in pdata:
                setattr(self,att,pdata[att])
        if USE_LTSP_DATA:
            is_ltsp=random.randint(0,1)
            if (self.real_flavour == 'client'):
                if (is_ltsp == 1):
                    self.ltsp=True
                    r=random.randint(0,len(LTSP_MODES)-1)
                    self.mode=LTSP_MODES[r]
                else:
                    self.ltsp=False
                    self.mode='FAT'
            else:
                self.ltsp=False
                self.mode='FAT'

    def gen_platform_data(self):
        data = {}
        rnd=random.randint(1,16000)
        data['arch']=ARCHS[rnd%2]
        data['mem']=str(rnd*1024)
        data['vga']='VGA '+ data['mem'][0:2]
        data['cpu']='CPU '+ data['mem'][1:3]
        data['ncpu']=str((rnd%3)+1)
        return data

    def info(self):
        print '{} {} {} {}'.format(self.mac,self.release,self.release_number,self.flavour)

    def gen_mac(self):
        global NCLIENTS,MAX_RANDOM_CLIENTS,MACS_USED

        if RANDOM and NCLIENTS <= MAX_RANDOM_CLIENTS:
            mac = "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))
            while mac in MACS_USED:
                mac = "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255),random.randint(0, 255),random.randint(0, 255))
            MACS_USED.append(mac)
            return mac
        else:
            mac = MAC_LIST.popleft()
            return mac

    def gen_rel_number(self):
        if self.release == '15':
            if RANDOM:
                if self.num == None:
                    self.num=random.randint(100,100+MAX_RELNUMBER)
                else:
                    self.num +=1
            else:
                if self.num == None:
                    self.num=100
                else:
                    self.num += 1
            rnum='15.05.0.{}'.format(self.num)
        else:
            if RANDOM:
                if self.year == None:
                    self.year=random.randint(16,16+(MAX_RELNUMBER/12))
                    self.month=random.randint(1,1+(MAX_RELNUMBER%12))
                    self.day=1
                else:
                    self.month+=1
            else:
                if self.year == None:
                    self.year=16
                    self.month=1
                    self.day=1
                else:
                    self.month+=1
            rnum='16.{}{:02d}{:02d}'.format(self.year,self.month,self.day)
        return rnum

    def gen_apps(self):
        global RANDOM,CLIENT_MAX_APPS,NAPPS
        l={}
        if RANDOM:
            napps=random.randint(0,CLIENT_MAX_APPS)
        else:
            napps=CLIENT_MAX_APPS
            start_app_at=random.randint(1,NAPPS-CLIENT_MAX_APPS+1)
        for i in range(napps):
            if RANDOM:
                apprandname='app'+str(random.randint(1,NAPPS))
                while apprandname in l:
                    apprandname='app'+str(random.randint(1,NAPPS))
                l[apprandname]=str(random.randint(1,10))
            else:
                apprandname='app'+str(start_app_at+i)
                l[apprandname]=10
        return (l,napps)

    def update(self):
        if DO_UPGRADES:
            self.upgrades()
        self.updates = self.updates +1
        orev = self.release_number
        self.release_number = self.gen_rel_number()
        if PRINT_UPDATES:
            if orev != self.release_number:
                print '{} updates from {} to {}'.format(self.mac,orev,self.release_number)

    def upgrades(self):
        prob = random.randint(0,100)
        if self.release == '15':
            if prob < UPGRADE_PROB:
                orev = self.release_number
                self.release = '16'
                self.release_number = self.gen_rel_number()
                if PRINT_UPDATES:
                    if orev != self.release_number:
                        print '{} upgrade from {} to {}'.format(self.mac,orev,self.release_number)
        prob = random.randint(0,100)
        if prob < UPGRADE_PROB:
            if RANDOM:
                fla=FLAVOURS[self.release][random.randint(0,len(FLAVOURS[self.release])-1)]
            else:
                fla=FLAVOURS[self.release][0]
            ofla = self.real_flavour
            self.flavour=fla['name']
            self.real_flavour=fla['real']
            if PRINT_UPDATES:
                if ofla != self.real_flavour:
                    print '{} change flavour from {} to {}'.format(self.mac,ofla,self.real_flavour)

    def get_data(self):
        tmp={}
        tmp['sab']=self.flavour
        tmp['vers']=self.release_number
        apps,napps=self.gen_apps()
        tmp['stats']=json.dumps(apps)
        tmp['uid']=self.mac
        if USE_PLATFORM_DATA:
            tmp['specs'] = {}
            tmp['specs']['mac']=self.mac
            tmp['specs']['arch']=self.arch
            tmp['specs']['mem']=self.mem
            tmp['specs']['vga']=self.vga
            tmp['specs']['cpu']={'model':self.cpu,'ncpus':self.ncpu}
            if USE_LTSP_DATA:
                if USE_LTSP_WITH_OLD_CLIENTS:
                    if random.randint(0,5) != 1:
                        tmp['specs']['subtype']={'LTSP':self.ltsp,'MODE':self.mode}
                else:
                    tmp['specs']['subtype']={'LTSP':self.ltsp,'MODE':self.mode}
        if self.inc_date > 0:
            d=datetime.today()+relativedelta(months=0-self.inc_date)
            tmp['date']=d.strftime('%Y-%m-%d %H:%M:%S')
        return ({'stats':json.dumps(tmp)},napps,apps)

class TEST():
    def __init__(self):
        self.client_list = deque()
        self.db = DB()
        self.stats={}
        self.pool=None
        self.lock=Lock()
        signal.signal(signal.SIGTERM,self.term_test)
        signal.signal(signal.SIGINT,self.term_test)

    def term_test(self,*args,**kwargs):
        global STATS_ON
        global exit_threads
        exit_threads=1
        STATS_ON=0
        print "Exitting.."
        sys.exit(1)

    def prepare(self):
        print 'Preparing clients... '
        pad=len(str(NCLIENTS))
        clean='\r\r\r\r\r\r\r\r\r\r';
        for i in range(NCLIENTS):
            sys.stderr.write(clean+str(i+1).zfill(pad))
            cli=CLIENT()
            #cli.info()
            self.client_list.append(cli)
        sys.stderr.write(clean+str(NCLIENTS)+' generated!\n')
        self.do_stats()
        self.print_stats()

    def prepare_threads(self):
        global MAX_THREADS
        if (NCLIENTS < MAX_THREADS):
            MAX_THREADS=NCLIENTS
            print("NEW NTHREADS {}".format(MAX_THREADS))
        self.pool = ThreadPool(processes=MAX_THREADS)
        sys.stderr.write('Created pool for {} threads, {} clients per thread\n'.format(MAX_THREADS,int(NCLIENTS/MAX_THREADS)))
        self.sess = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=CACHE_CONNECTIONS,pool_maxsize=MAX_THREADS+1,max_retries=3,pool_block=False)
        self.sess.mount('http://',adapter)

    def init_test(self):
        global STATS_ON
        self.prepare()
        #self.db.init_db()
        #self.db.close_db()
        self.prepare_threads()
        if STATS_ON and STATS_ON != 0:
            STATS_ON=1
            try:
                threading.Thread(target=self.time_stats).start()
            except:
                pass
        self.start()
        STATS_ON=0

    def do_stats(self):
        for rel in RELEASES:
            self.stats[rel]={}
            self.stats[rel]['nclients']=0
            self.stats[rel]['nclients_updated']=0
            self.stats[rel]['flavours']={}

        for cli in self.client_list:
            self.stats[cli.release]['nclients']=self.stats[cli.release]['nclients']+1
            self.stats[cli.release]['nclients_updated']=self.stats[cli.release]['nclients_updated']+cli.updates
            if cli.real_flavour not in self.stats[cli.release]['flavours']:
                self.stats[cli.release]['flavours'][cli.real_flavour]=1
            else:
                self.stats[cli.release]['flavours'][cli.real_flavour]=self.stats[cli.release]['flavours'][cli.real_flavour]+1

    def print_stats(self):
        print ''
        for rel in RELEASES:
            print 'RELEASE {}: {} clients ({} updated)'.format(rel,self.stats[rel]['nclients'],self.stats[rel]['nclients_updated'])
            keys=self.stats[rel]['flavours'].keys()
            keys.sort()
            for key in keys:
                print '\t{} : {}'.format(key,self.stats[rel]['flavours'][key])
            print ''


    def time_stats(self):
        global STATS_ON,NPET,PAUSE_SHOW_STATS,SUCCESS,DATE_ROUNDS
        global NCLIENTS,LOOPS
        print "STATS_ON"
        total=NCLIENTS*LOOPS
        old_npet=[]*9
        f=lambda x,y: x+y
        while STATS_ON and STATS_ON != 0:
            if not PAUSE_SHOW_STATS:
                old_npet.append(NPET)
                med_npet=reduce(f,old_npet)/len(old_npet)
                old_npet=old_npet[1-len(old_npet):]
                sys.stderr.write(' '*20+'\r'*20+'{} r/s ETA:{} secs'.format(int(med_npet),int((total-SUCCESS)/(med_npet+1))))
                self.lock.acquire()
                NPET=0
                self.lock.release()
            time.sleep(1)

    def start(self):
        global APPS_SENT,ALL_BY_APP,PAUSE_SHOW_STATS,PAUSE_WITH_DATE_ROUNDS,CURRENT_DATE_ROUND,CURRENT_LOOP_ROUND
        global STATS_ON,SHOW_BY_APP,NPET,SUCCESS,FAILED,REDO,UPDATED,UPDATED_TOTAL


        #DATE_DATA=[]
        ALL_BY_APP={}
        for k in range(DATE_ROUNDS):
          CURRENT_DATE_ROUND=k
          NPET=0
          SUCCESS=0
          FAILED=0
          REDO=0
          UPDATED=0
          start_time=time.time()
          if (k > 0):
            for cli in self.client_list:
                cli.inc_date+=1
          TOTAL_SENT={}
          ALL_SENT={}
          for rel in ['15','16']:
            TOTAL_SENT[rel]={}
            ALL_SENT[rel]={}
            for fla in ['desktop','server','client','other']:
                TOTAL_SENT[rel][fla]=0
                ALL_SENT[rel][fla]=0
                ALL_SENT[rel][fla+'apps']={}

          for i in range(LOOPS):
              CURRENT_LOOP_ROUND=i
              UPDATED_TOTAL=UPDATED
              sys.stderr.write('\nRound {}/{} Date round {}/{} ...\n'.format(i+1,LOOPS,k+1,DATE_ROUNDS))
              APPS_SENT={}
              for rel in ['15','16']:
                  APPS_SENT[rel]={}
                  for fla in ['desktop','server','client','other']:
                      APPS_SENT[rel][fla]=0
                      APPS_SENT[rel][fla+'apps']={}
              try:
                self.pool.map_async(self.thread_code,self.client_list).get(timeout=1000000)
              except:
                sys.stderr.write('Fatal error when threading\n')

	      for rel in ['15','16']:
		  for fla in ['desktop','server','client','other']:
		      if not STATS_ON and DEBUG and DEBUG > 1:
		         sys.stderr.write('\t{}:{} ({} apps sent ((tmp_packages count)insert or update))\n'.format(rel,fla,APPS_SENT[rel][fla]))
		      TOTAL_SENT[rel][fla]=TOTAL_SENT[rel][fla]+APPS_SENT[rel][fla]
		      ALL_SENT[rel][fla]=ALL_SENT[rel][fla]+APPS_SENT[rel][fla]
		      for app in APPS_SENT[rel][fla+'apps']:
			  if app not in ALL_SENT[rel][fla+'apps']:
			      ALL_SENT[rel][fla+'apps'][app]=APPS_SENT[rel][fla+'apps'][app]
			  else:
			      ALL_SENT[rel][fla+'apps'][app]+=APPS_SENT[rel][fla+'apps'][app]
	      if not STATS_ON:
	        sys.stderr.write('\n')

          #STATS_ON=0
	  total=0
	  print "\n\nTOTAL APPS SENT AFTER DATE_ROUND {}/{}\n".format(k+1,DATE_ROUNDS)
	  other_all_sent={}
          #mini_date_data={}
	  for rel in ['15','16']:
	      total_rel=0
	      #mini_date_data[rel]={}
	      for fla in ['desktop','server','client','other']:
		  print "\tBY {} {} : {} sent (insert or update)(tmp_packages count)".format(rel,fla,ALL_SENT[rel][fla])
		  total_rel=total_rel+ALL_SENT[rel][fla]
		  if fla == 'other':
		      for x in ALL_SENT[rel][fla+'apps']:
			  if x in other_all_sent:
			      other_all_sent[x]+=ALL_SENT[rel][fla+'apps'][x]
			  else:
			      other_all_sent[x]=ALL_SENT[rel][fla+'apps'][x]
		  else:
		      sorted_x=sorted(ALL_SENT[rel][fla+'apps'].items(),key=operator.itemgetter(1),reverse=True)
		      #mini_date_data[rel][fla]=ALL_SENT[rel][fla+'apps'];
		      for x in sorted_x[0:10]:
			print "\t\t{}:{}".format(x[0],x[1])
	      print "\tTOTAL RELEASE {} : {} sent (insert or update)(tmp_packages count)".format(rel,total_rel)
	      total=total+total_rel
	  
	  print "\tOTHER (combined 15,16):"
	  sorted_x=sorted(other_all_sent.items(),key=operator.itemgetter(1),reverse=True)
	  for x in sorted_x[0:10]:
	      print "\t\t{}:{}".format(x[0],x[1])
          #mini_date_data['other']={'other':other_all_sent}
	  #DATE_DATA.append(mini_date_data)
	  print "TOTAL ALL RELEASES : {} sent (insert or updated)(tmp_packages count)".format(total)
          if SHOW_BY_APP:
                sorted_apps=sorted(ALL_BY_APP.items(),key=operator.itemgetter(1),reverse=True)
                print "\n~~~~~~~~~~~~~~~~~~~\n~~RESUME BY APPS:~~\n~~~~~~~~~~~~~~~~~~~\n"
                for x in sorted_apps[0:20]:
                    print "\t\t{}:{}".format(x[0],x[1])
          elapsed_time=time.time()-start_time
          print "\nEND DATE ROUND {}/{}\nCLIENTS UPDATED:{}\nTOTAL_CLIENTS:{}\nSUCCESS:{} req\nFAILED:{} req\nREDO:{} req\nELAPSED:{} secs\n{} req/s\n".format(k+1,DATE_ROUNDS,UPDATED_TOTAL,NCLIENTS+UPDATED_TOTAL,SUCCESS,FAILED,REDO,int(elapsed_time),int(SUCCESS/elapsed_time))
	  if PAUSE_WITH_DATE_ROUNDS and DATE_ROUNDS > 1 and k != DATE_ROUNDS -1:
	    PAUSE_SHOW_STATS=True
	    readed=None
	    while readed != '\n':
                print "Now change date into server and press enter"
	        readed=sys.stdin.readline()
	    PAUSE_SHOW_STATS=False
          '''
          print "\n~~~~~~~~~~~~~~~~~~~\n~~~~  RESUME:  ~~~~\n~~~~~~~~~~~~~~~~~~~\n"
          #print(json.dumps(DATE_DATA))
          #print ""
          k=0
          for l in DATE_DATA:
             #print "another round {}".format(k)
             if k==0:
                continue;
             for r in l:
                 #print "release: {}".format(r)
                 d=l[r]
                 for f in d:
                     #print "flavour {}".format(f)
                     for app in d[f]:
                         value=d[f][app]
                         #print "\t\t{}: {}".format(app,d[f][t])
                         if app in l[0][r][f]:
                            DATE_DATA[0][r][f]+=value
                         else:
                            DATE_DATA[0][r][f]=value
             k+=1
          for r in DATE_DATA[0]:
            print "TOTAL Release {}".format(r) 
            for f in DATE_DATA[0][r]:
               sorted_x=sorted(DATE_DATA[0][r][f].items(),key=operator.itemgetter(1),reverse=True)
               print "\tFlavour {}".format(f)
               for x in sorted_x[0:10]:
                  print "\t\t{}: {}".format(x[0],x[1])
'''



    def thread_code(self,client):
            global exit_threads

            if exit_threads and exit_treads==1:
                return

            global APPS_SENT,TMP,ALL_BY_APP
            global NPET,SUCCESS,FAILED,REDO,UPDATED,CURRENT_LOOP_ROUND,LOOPS
            try:
                data,napps,lapps=client.get_data()
            except:
                pass

            try:
                do=False
                i=5
                error_replay = False
                while i > 0:
                    try:
                        r = self.sess.post(HOST,data=data,headers=HEADERS,timeout=TIMEOUT)
                        i = 0
                    except Exception as e:
                        print 'R'+e+"\n"
                        do=True
                        time.sleep(SLEEP_THREAD_TIME)
                    if do:
                        self.lock.acquire()
                        REDO+=1
                        time.sleep(SLEEP_FAIL_SENDING)
                        self.lock.release()
                        i -= 1
                        if i == 0:
                            error_replay = True

                    #r = self.sess.post(HOST,data=data,headers=HEADERS,timeout=TIMEOUT)

                #sys.stderr.write('.')

                if SLEEP_THREAD_TIME and SLEEP_THREAD_TIME > 0:
                    time.sleep(SLEEP_THREAD_TIME)

                if error_replay:
                    self.lock.acquire()
                    FAILED+=1
                    self.lock.release()
                    raise Exception('Fail Sending')

                if r.text != 'OK':
                    self.lock.acquire()
                    FAILED+=1
                    self.lock.release()
                    print '{}'.format(data)
                    raise Exception('Reply NOK')

                self.lock.acquire()
                NPET+=1
                SUCCESS+=1
                APPS_SENT[str(client.release)][client.real_flavour] = APPS_SENT[str(client.release)][client.real_flavour] + napps
                for app in lapps:
                    if app not in ALL_BY_APP:
                        ALL_BY_APP[app]=int(lapps[app])
                    else:
                        ALL_BY_APP[app]+=int(lapps[app])
                    if app not in APPS_SENT[str(client.release)][client.real_flavour+'apps']:
                        APPS_SENT[str(client.release)][client.real_flavour+'apps'][app]=int(lapps[app])
                    else:
                        APPS_SENT[str(client.release)][client.real_flavour+'apps'][app]+=int(lapps[app])
                self.lock.release()

            except Exception as e:
                sys.stderr.write('E'+str(e))

            if LOOPS > 1 and CLIENT_UPDATE_FREQ > random.randint(0,100):
                if CURRENT_LOOP_ROUND < LOOPS -1:
                    self.lock.acquire()
                    UPDATED+=1
                    self.lock.release()
                    client.update()

if __name__ == "__main__":
    tst = TEST()
    tst.init_test()