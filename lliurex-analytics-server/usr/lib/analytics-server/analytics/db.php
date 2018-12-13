<?php
$USE_CACHE = true;
class Cache{
    private $cache_file;
    private $cache_dir;
    private $data_file;
    private $data;
    private $cache_timeout=3600;

    function Cache(){
        $this->cache_dir = sys_get_temp_dir();
        $this->cache_file = "cache_analytics.db.tmp";
        $this->datafile=$this->cache_dir.'/'.$this->cache_file;
        $this->data = array();
    }
    function readFile(){
        if (is_file($this->datafile) and is_writable($this->datafile)){
            $this->filecontents = file_get_contents($this->datafile);
        }else{
            // do nothing or throw error
            return false;
        }
        return true;
    }
    function newFile($data=array()){
        // create new file
        $obj=$data;
        $json='';
        try{
            $json=json_encode($obj);
        }catch(Exception $e){
            return false;
        }
        file_put_contents($this->datafile,$json);
    }
    function parseJson(){
        try{
            $json=json_decode($this->filecontents,true);
            $this->data=$json;
        }catch(Exception $e){
            return false;
        }
        return true;
    }
    function process(){
        $continue = false;
        if ($this->readFile()){
            $continue = true;
        }else{
            $this->newFile();
            if ($this->readFile()){
                $continue=true;
            }
        }
        if (! $continue){
            return false;
        }
        if (! $this->parseJson()){
            return false;
        }
        return true;
    }
    function get($key){
        global $USE_CACHE;
        if (! $USE_CACHE){
            return false;
        }
        if (! $this->process()){
            return false;
        }
        try{
            $data=$this->data;
            if ($data == null or ! is_array($data) or ! array_key_exists($key,$data))
                return false;
            $data=$data[$key];
            if (time() - (int)$data['timestamp'] > $this->cache_timeout){
                return false; //'invalid';
            }else{
                return $data['value'];
            }
        }catch(Exception $e){
            return false;
        }
    }
    function invalidate($key){
        global $USE_CACHE;
        if (! $USE_CACHE){
            return false;
        }
        if (! $this->process()){
            return false;
        }
        try{
            $data=$this->data;
            if ($data == null or ! is_array($data) or ! array_key_exists($key,$data))
                return false;
            if (array_key_exists($key,$this->data)){
                unset($this->data[$key]);
                return $this->newFile($this->data);
            }else{
                return false;
            }
        }catch(Exception $e){
            return false;
        }
    }
    function store($obj,$key){
        if (! $this->process()){
            return false;
        }
        try{
            $this->data[$key]=['timestamp'=>time(),'value'=>$obj];
            return $this->newFile($this->data);
        }catch(Exception $e){
            return false;
        }
    }
}

class DB{

     private $dbhost;
     private $dbname;
     private $dbuser;
     private $dbpass;
     private $ka_file='/var/run/analyticsd.keepalive';
     private $alias;
     public $dbconn;

     function DB(){
         require_once('config.php');
         global $dbhost,$dbname,$dbpass,$dbuser,$distros,$swversion;

         $this->dbhost=$dbhost;
         $this->dbname=$dbname;
         $this->dbpass=$dbpass;
         $this->dbuser=$dbuser;
         $this->swversion=$swversion;
         $this->alias=array();
         $this->info_distro=json_decode($distros,true);
         if ($this->info_distro == NULL){
             die('Error: Wrong json in Config.php');
         }
         $this->init_dates();
         $this->times=0;
     }
     function init_dates($range=NULL){
         $this->dates=array();
         $this->dates['today']=date("Y-m-d");
         $this->dates['first_current']=date("Y-m-01");
         $this->dates['last_old']=date("Y-m-d",strtotime($this->dates['first_current']." -1 days"));
         $this->dates['first_old']=date("Y-m-01",strtotime($this->dates['last_old']));
         $this->dates['last_very_old']=date("Y-m-d",strtotime($this->dates['first_old']." -1 days"));
         $this->dates['first_very_old']=date("Y-m-01",strtotime($this->dates['last_very_old']));
         $this->dates['date_current']="(date between '".$this->dates['first_current']."' and '".$this->dates['today']."')";
         $this->dates['date_old']="(date between '".$this->dates['first_old']."' and '".$this->dates['last_old']."')";
         $this->dates['date_very_old']="(date between '".$this->dates['first_very_old']."' and '".$this->dates['last_very_old']."')";
         $this->dates['date_range_last_three_months']="(date between '".$this->dates['first_very_old']."' and '".$this->dates['today']."')";

         if ($range != NULL){
            $y=intval($range['year']);
            $m=intval($range['month']);
            $w=intval($range['window']);
            $this->dates['init_range']=date("Y-m-01",strtotime($y.'-'.$m.'-01'));
            $this->dates['end_range']=date("Y-m-01",strtotime($y.'-'.$m.'-01 +'.$w.' month'));
            $this->dates['end_range']=date("Y-m-d",strtotime($this->dates['end_range'].' -1 day'));
            if (strtotime($this->dates['end_range']) > strtotime($this->dates['today'])){
                $this->dates['end_range']=$this->dates['today'];
            }
            $this->dates['custom_range']="(date between '".$this->dates['init_range']."' and '".$this->dates['end_range']."')";
         }
     }
     function connect(){
        $this->dbconn=new mysqli($this->dbhost, $this->dbuser , $this->dbpass, $this->dbname);
        if ($this->dbconn->connect_error) {
            die('Connect Error:'. $this->dbconn->connect_error);
        }
     }
     function disconnect(){
         $this->dbconn->close();
     }
     function init_trans(){
         $this->dbconn->autocommit(FALSE);
         $this->dbconn->begin_transaction(MYSQLI_TRANS_START_READ_WRITE);
     }

    function send_data($user,$version,$sabor,$apps,$specs,$date=''){
        $spec_sql_names = '';
        $spec_sql_values = '';

        $ltsp_sql_names = '';
        $ltsp_sql_values = '';

        $use_data=array();
        $use_name=array();
        if ($specs != false){
            if (array_key_exists('arch',$specs)){
                $arch = $specs['arch'];
                $use_data[]="'$arch'";
                $use_name[]='arch';
            }
            if (array_key_exists('mem',$specs)){
                $mem = $specs['mem'];
                if (is_numeric($mem)){
                    $mem=(int)$mem;
                }
                $use_data[]=$mem;
                $use_name[]='mem';
            }
            if (array_key_exists('vga',$specs)){
                $vga = substr($specs['vga'],0,80);
                $use_name[]='vga';
                $use_data[]="'$vga'";
            }
            if (array_key_exists('cpu',$specs)){
                if (array_key_exists('model',$specs['cpu'])){
                    $cpu = substr($specs['cpu']['model'],0,80);
                    $use_name[]='cpu';
                    $use_data[]="'$cpu'";
                }
                if (array_key_exists('ncpus',$specs['cpu'])){
                    $ncpu = $specs['cpu']['ncpus'];
                    if (is_numeric($ncpu)){
                        $ncpu=(int)$ncpu;
                    }
                    $use_name[]='ncpu';
                    $use_data[]=$ncpu;
                }
            }
            if (count($use_data) > 0){
                $spec_sql_names = ',';
                $spec_sql_names .= implode(',',$use_name);
                $spec_sql_values = ',';
                $spec_sql_values .= implode(',',$use_data);
            }else{
                $spec_sql_names = '';
                $spec_sql_values = '';
            }
            $use_data=array();
            $use_name=array();
            if (array_key_exists('subtype',$specs)){
                if (array_key_exists('LTSP',$specs['subtype'])){
                    $ltsp = $specs['subtype']['LTSP'];
                    if ($ltsp){
                        $ltsp='TRUE';
                    }else{
                        $ltsp='FALSE';
                    }
                    $use_name[]='ltsp';
                    $use_data[]=$ltsp;
                }
                if (array_key_exists('MODE',$specs['subtype'])){
                    $ltsp_mode = $specs['subtype']['MODE'];
                    $ltsp_mode = substr($ltsp_mode,0,4);
                    if (strtolower($ltsp_mode) != 'null'){
                        $use_name[]='mode';
                        $use_data[]="'$ltsp_mode'";
                    }
                }
            }
            if (count($use_name) > 0){
                $ltsp_sql_names = ',';
                $ltsp_sql_names .= implode(',',$use_name);
                $ltsp_sql_values = ',';
                $ltsp_sql_values .= implode(',',$use_data);
            }else{
                $ltsp_sql_names = '';
                $ltsp_sql_values = "";
            }
        }
        if ($date == ''){
            $sql="INSERT INTO tmp_clients(user,version,sabor,status $spec_sql_names $ltsp_sql_names) values ('$user','$version','$sabor',0 $spec_sql_values $ltsp_sql_values)";
        }else{
            $sql="INSERT INTO tmp_clients(user,version,sabor,status,date $spec_sql_names $ltsp_sql_names) values ('$user','$version','$sabor',0,'$date' $spec_sql_values $ltsp_sql_values)";
        }
        $retry=1;
        $done=false;
        $cli_id=false;
        while (! $done and $retry < 4){
            $res=$this->dbconn->query($sql);
            if ($res){
                $cli_id=$this->dbconn->insert_id; 
                $done=true;
            }else{
                $retry+=1;
                sleep($retry);
            }
        }
        if ($retry == 4 or $cli_id == false)
            throw new Exception('Error sending client data: '.$this->dbconn->error);
        $err_apps=false;
        $err_exception=false;
        if (count($apps) != 0){
            if ($date == ''){
                $sql="insert into tmp_packages(client,app,value) values";
            }else{
                $sql="insert into tmp_packages(client,app,value,date) values";
            }
            $values=array();
            // Prevent DoS attack
            $i = 1000;
            foreach ($apps as $app => $value){
                // Max 1000 apps
                if ( $i > 0 ){
                    $i = $i - 1;
                }else{
                    throw new Exception('*** DoS detected, aborting more processing on this request ***');
                } 

                if (trim($app) == '' or trim($value) == ''){
                    $err_apps=true;
                    $err_exception=new Exception('Wrong application values');
                    continue;
                }
                if ($date == ''){
                    $values[]="($cli_id,'$app',$value)";
                }else{
                    $values[]="($cli_id,'$app',$value,'$date')";
                }
            }
            if (count($values) > 0){
                $sql.=implode(',',$values);
                $done=false;
                $retry=1;
                while (! $done and $retry < 4){
                    $res=$this->dbconn->query($sql);
                    if ($res){
                        $done=true;
                    }else{
                        $retry += 1;
                        sleep($retry);
                    }
                }
                if ($retry == 4 or ! $done){
                    $err_apps=true;
                    $err_exception=new Exception('Error sending client app data: '.$this->dbconn->error.' QUERY='.$sql);
                }
            }
        }
        //End operations
        $sql = "Update tmp_clients set status=1 where id = $cli_id and status=0";
        $retry=1;
        $done=false;
        while (! $done and $retry < 4){
            $res=$this->dbconn->query($sql);
            if ($res){
                $done=true;
            }else{
                $retry+=1;
                sleep($retry);
            }
        }
        if ($retry == 4 or $cli_id == false){
            throw new Exception('Error commiting client data: '.$this->dbconn->error);
        }
        if ($err_apps){
            throw $err_exception;
        }
    }

     private function load_alias(){
         $sql="SELECT name,alias from Alias";
         $result=$this->dbconn->query($sql);
         while($row=$result->fetch_array(MYSQLI_ASSOC)){
             $this->alias[$row['name']]=$row['alias'];
         }
     }
        function get_system_data(){
            $sql="select * from Config";
            $result=$this->dbconn->query($sql);
            if ($result){
                $tmp=[];
                while ($row=$result->fetch_array(MYSQLI_ASSOC)){
                    $tmp[$row['name']]=$row['value'];
                }
                return json_encode($tmp);
            }
        }
    function execute_sql_array($arr,$fkey=false){
	if (! is_array($arr)){
		return false;
	}
	$time=0;
	foreach ($arr as $key => $value){
		if (! $fkey or $key == $fkey){
			$stime=microtime(true);
			$result=$this->dbconn->query($value);
			if (!$result){
				die("Error in sql '".$value."' -> ".$this->dbconn->error);
			}
			$time += microtime(true) - $stime;
		}
	}
	return $time;
    }
    function get_extended_data($app){
        global $swversion;

        $this->times=0;
	$cache = new Cache;
	$use_memtable=true;
	$use_views=false;
	$split_tables=false;
         // CLIENT UPDATES
	$sql_compat_tables=array();
	$table = 'Client_Versions';
	if ($use_views){
		$split_tables=true;
		$sql_compat_tables[]="create or replace view cv as (select Client_uid,date,Releases_name,Flavours_name,string_release from $table)";
		$sql_compat_tables[]="create or replace view cv_a as (select Client_uid,date,Releases_name,Flavours_name,arch from $table)";
		$sql_compat_tables[]="create or replace view cv_m as (select Client_uid,date,Releases_name,Flavours_name,mem from $table)";	
		$sql_compat_tables[]="create or replace view cv_c as (select Client_uid,date,Releases_name,Flavours_name,ncpu from $table)";
		$sql_compat_tables[]="create or replace view cv_l as (select Client_uid,date,Releases_name,Flavours_name,ltsp,mode from $table)";
		$table = 'cv';
	}
	if ($use_memtable){
		if (! $split_tables){
			$sql_compat_tables[]="create temporary table if not exists cv engine=memory as (select Client_uid,date,Releases_name,Flavours_name,string_release,arch,mem,ncpu,ltsp,mode from $table)";
		//	$sql_compat_tables[]="alter table cv add primary key(Client_uid,date,Releases_name,Flavours_name,arch,mem,ncpu,uuid)";	
		//	$sql_compat_tables[]="create index a on cv(Client_uid,date) using btree";
		//	$sql_compat_tables[]="create index b on cv(arch,date,) using btree";
		//	$sql_compat_tables[]="create index c on cv(date,mem) using btree";
		//	$sql_compat_tables[]="create index d on cv(date,ncpu) using btree";
		}else{
			$sql_compat_tables[]="create temporary table if not exists cv engine=memory as (select Client_uid,date,Releases_name,Flavours_name,string_release from $table)";
			$sql_compat_tables[]="create temporary table if not exists cv_a engine=memory as (select Client_uid,date,Releases_name,Flavours_name,arch from $table)";
			$sql_compat_tables[]="create temporary table if not exists cv_m engine=memory as (select Client_uid,date,Releases_name,Flavours_name,mem from $table)";	
			$sql_compat_tables[]="create temporary table if not exists cv_c engine=memory as (select Client_uid,date,Releases_name,Flavours_name,ncpu from $table)";
			$sql_compat_tables[]="create temporary table if not exists cv_l engine=memory as (select Client_uid,date,Releases_name,Flavours_name,ltsp,mode from $table)";
		}
	}
	if ($use_memtable or $use_views){
		$table='cv';
	}
	if($split_tables){
		$table_a=$table.'_a';
		$table_m=$table.'_m';
		$table_c=$table.'_c';
		$table_l=$table.'_l';
	}else{
		$table_a=$table;
		$table_m=$table;
		$table_c=$table;
		$table_l=$table;
	}
	$sql_compat_tables[]="create temporary table if not exists dates engine=memory as (select * from (select year,month from (select year,month from (select year,month from (select year(now()) as year union all select year(date_sub(now(),interval 1 year)))years inner join (select 1 as month union all select 2 union all select 3 union all select 4 union all select 5 union all select 6 union all select 7 union all select 8 union all select 9 union all select 10 union all select 11 union all select 12)months)dates where str_to_date(concat(year,'-',month,'-01'),'%Y-%m-%d') >= date_sub(now(),interval 1 year) and str_to_date(concat(year,'-',month,'-01'),'%Y-%m-%d') < now())compat)dates order by year, month)";
	$sql_compat_tables[]="create temporary table if not exists compat_rf engine=memory as (select * from dates join (select name as rel from Releases where Releases.name != 'other')rels join (select name as fla from Flavours)flas)";
	$sql_compat_tables[]="create temporary table if not exists compat_rfa engine=memory as (select * from compat_rf join (select 'x86_64' as arch union all select 'i686' union all select 'UNKN')arches)";
	$sql_compat_tables[]="create temporary table if not exists compat_t engine=memory as (select * from dates join(select 0 as type union all select 1 union all select 'UNKN') types)";
	$sql_compat_tables[]="create temporary table if not exists compat_m engine=memory as (select * from dates join (select 'THIN' as mode union all select 'SEMI' union all select 'FAT' union all select 'UNKN') types)";
	
	$sql_nhosts=array();
	$sql_nhosts[]="/*Num total hosts detailed*/ create temporary table if not exists nhosts_detail engine=memory as (select * from compat_rf left join (select year,month,rel,fla,ifnull(count(*),0) as total_hosts from (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,Client_uid from (select Client_uid,Releases_name,Flavours_name,date from $table order by date desc)t group by year(date),month(date),Releases_name,Flavours_name,Client_uid)unique_last_clients group by year,month,rel,fla)detailed using (year,month,rel,fla));";
	$sql_nhosts[]="/*Num total hosts*/ create temporary table if not exists nhosts engine=memory as (select year,month,sum(total_hosts) as total_hosts from nhosts_detail group by year,month);";
	$sql_upd=array();
	$sql_upd[]="/*Num host single entry*/ create temporary table if not exists single_entry engine=memory as (select year,month,ifnull(single_entry,0) as single_entry from dates left join (select year,month,count(*) as single_entry from (select year(date) as year, month(date) as month from $table group by year(date),month(date),Client_uid having count(*) = 1)a group by year,month)singles using(year,month));";
	$sql_upd[]="/*A+B*/ create temporary table if not exists ab engine=memory as (select distinct year,month,Client_uid from ( select Distinct Client_uid,Releases_name,year(date) as year,month(date) as month from $table)t group by year,month,Client_uid having count(*) > 1);";
	$sql_upd[]="create index a on ab (Client_uid,year,month) using btree;";
	$sql_upd[]="/*B+C+D*/ create temporary table if not exists bcd engine=memory as (select distinct year,month,Client_uid from ( select Distinct Client_uid,Flavours_name,year(date) as year,month(date) as month from $table)t group by year,month,Client_uid having count(*) > 1);";
	$sql_upd[]="create index a on bcd (Client_uid,year,month) using btree;";	
	$sql_upd[]="/* B */ create temporary table if not exists b engine=memory as (select * from ab join bcd using(year,month,Client_uid));";
	$sql_upd[]="/* A */ create temporary table if not exists a engine=memory as (select * from ab left join bcd using(year,month,Client_uid) where bcd.Client_uid is null); ";
	$sql_upd[]="/* A+B+C */ create temporary table if not exists abc_plus_part_e engine=memory as (select distinct year,month,Client_uid from ( select Distinct Client_uid,string_release,year(date) as year,month(date) as month from $table)t group by year,month,Client_uid having count(*) > 1);";
	$sql_upd[]="create index a on abc_plus_part_e (Client_uid,year,month) using btree;";
	$sql_upd[]="/* C+D */ create temporary table if not exists cd engine=memory as (select * from ab right join bcd using(year,month,Client_uid) where ab.Client_uid is null);";
	$sql_upd[]="create index a on cd (Client_uid,year,month) using btree;";
	$sql_upd[]="/* D */ create temporary table if not exists d engine=memory as (select * from cd left join abc_plus_part_e using(year,month,Client_uid) where abc_plus_part_e.Client_uid is null);";
	$sql_upd[]="create index a on d (Client_uid,year,month) using btree;";
	$sql_upd[]="/* C */ create temporary table if not exists c engine=memory as (select * from cd left join d using(year,month,Client_uid) where d.Client_uid is null );";
	$sql_upd[]="create temporary table if not exists na engine=memory as (select year,month,ifnull(a,0) as a from dates left join (select year,month,count(*) as a from a group by year,month)t using(year,month));";
	$sql_upd[]="create temporary table if not exists nb engine=memory as (select year,month,ifnull(b,0) as b from dates left join (select year,month,count(*) as b from b group by year,month)t using(year,month));";
	$sql_upd[]="create temporary table if not exists nc engine=memory as (select year,month,ifnull(c,0) as c from dates left join (select year,month,count(*) as c from c group by year,month)t using(year,month));";
	$sql_upd[]="create temporary table if not exists nd engine=memory as (select year,month,ifnull(d,0) as d from dates left join (select year,month,count(*) as d from d group by year,month)t using(year,month));";
	$sql_upd[]="/* temp */ create temporary table tmp_resume engine=memory as (select * from dates left join nhosts using(year,month) join single_entry using(year,month) join na using(year,month) join nb using(year,month) join nc using(year,month) join nd using(year,month));";
	$sql_upd[]="/* resume */ create temporary table resume engine=memory as (select year,month,total_hosts,single_entry,total_hosts-single_entry as target_hosts,a,b,c,d, total_hosts-single_entry-a-b-c-d as e from tmp_resume);";
	
	$sql_targets=array();
	$sql_targets['arch']="create temporary table if not exists target_arch engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,ifnull(if( arch like 'NULL',NULL,arch),'UNKN') as arch,count(distinct Client_uid) as total from $table_a group by year,month,Releases_name,Flavours_name,arch)";
	$sql_targets['memnull']="create temporary table if not exists target_memnull engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_m where mem is null and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
        $sql_targets['mem2G']="create temporary table if not exists target_mem2G engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_m where mem < 2048000 and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
	$sql_targets['mem4G']="create temporary table if not exists target_mem4G engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_m where mem > 2048000 and mem < 4096000 and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
	$sql_targets['mem8G']="create temporary table if not exists target_mem8G engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_m where mem > 4096000 and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
	$sql_targets['cpunull']="create temporary table if not exists target_cpunull engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_c where ncpu is null and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
        $sql_targets['cpu_mono']="create temporary table if not exists target_cpu_mono engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_c where ncpu < 2 and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
        $sql_targets['cpu_dual']="create temporary table if not exists target_cpu_dual engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_c where ncpu > 1 and ncpu < 5 and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
	$sql_targets['cpu_more']="create temporary table if not exists target_cpu_more engine=memory as (select year(date) as year,month(date) as month,Releases_name as rel,Flavours_name as fla,count(distinct Client_uid) as total from $table_c where ncpu  > 4 and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,rel,fla)";
	$sql_targets['ltsp_type']="create temporary table if not exists target_type engine=memory as(select year(date) as year,month(date) as month,ifnull(ltsp,'UNKN') as type,count(distinct Client_uid) as total from $table_l where Flavours_name = 'client' and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,ltsp)";
	$sql_targets['ltsp_mode']="create temporary table if not exists target_mode engine=memory as (select year(date) as year,month(date) as month,ifnull(mode,'UNKN') as mode,count(distinct Client_uid) as total from $table_l where Flavours_name = 'client' and date >= DATE_SUB(NOW(),interval 1 year) group by year,month,mode)";
	

	$exec_time=$this->execute_sql_array($sql_compat_tables);
	if ($exec_time){
		$this->times+=$exec_time;
	}

	$sql_upd_show="select * from resume order by year desc, month desc";
	$cache_key='updates';
    	$data = $cache->get($cache_key);
	$updated_nhosts=false;
    	$stime=microtime(true);
	if ($data != false){
		$num_updates_month=$data['num_updates_month'];
		$machines_month=$data['machines_month'];
		$change_releases=$data['change_releases'];
		$change_flavour=$data['change_flavour'];
	}else{
		if($this->execute_sql_array($sql_nhosts)){
			$updated_nhosts=true;
	    	}
		$this->execute_sql_array($sql_upd);
		$result=$this->dbconn->query($sql_upd_show);
		if ($result){
        		$machines_month=[0,0,0,0,0,0,0,0,0,0,0,0];
			$num_updates_month=[0,0,0,0,0,0,0,0,0,0,0,0];
			$change_releases=[0,0,0,0,0,0,0,0,0,0,0,0];
			$change_flavour=[0,0,0,0,0,0,0,0,0,0,0,0];
			$num_updates_month=array();
			$this->times+=microtime(true)-$stime;
			$i=0;
			$tmp=[];
 			while($row=$result->fetch_array(MYSQLI_ASSOC)){
				$machines_month[$i]=intval($row['total_hosts']);
				$change_releases[$i]=intval($row['a'])+intval($row['b']);
				$change_flavour[$i]=intval($row['c'])+intval($row['d']);
				$num_updates_month[$i]=intval($row['e']);
				$i++;
 			}
    			$cache->store(array('num_updates_month'=>$num_updates_month,'machines_month'=>$machines_month,'change_releases'=>$change_releases,'change_flavour'=>$change_flavour),$cache_key);
		}else{
			$num_updates_month=$this->dbconn->error;
			$machines_month=$this->dbconn->error;
			$change_releases=$this->dbconn->error;
			$change_flavour=$this->dbconn->error;
		}
	}
	$sql="select * from nhosts_detail order by year desc, month desc;";
	$cache_key='nhosts_detail';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_month=$data;
        }else{
	    if (!$updated_nhosts){
	        $this->execute_sql_array($sql_nhosts);
	    }
            $result=$this->dbconn->query($sql);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_month=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total_hosts']);
                }
		foreach($tmp as $date_value){
			$clients_month[]=$date_value;
		}
                $cache->store($clients_month,$cache_key);
            }else{
                $clients_month=$this->dbconn->error;
            }
        }
	// architecture
	$sql_arch="select compat_rfa.year,compat_rfa.month,compat_rfa.rel,compat_rfa.fla,compat_rfa.arch,ifnull(target_arch.total,0) as total from compat_rfa left join target_arch using(year,month,rel,fla,arch) order by year desc,month desc,rel asc,fla asc, arch asc";
	$cache_key='extended_arch';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_arch=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'arch');
            $result=$this->dbconn->query($sql_arch);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_arch=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
			$date=$row['year'].'_'.$row['month'];
                	$tmp[$date][$row['rel']][$row['fla']][strtolower($row['arch'])]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_arch[]=$d;
		}
                $cache->store($clients_arch,$cache_key);
            }else{
                $clients_arch=$this->dbconn->error;
            }
        }
        // memory
	$sql_memnull="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_memnull.total,0) as total from compat_rf left join target_memnull using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_null';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_memnull=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'memnull');
            $result=$this->dbconn->query($sql_memnull);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_memnull=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_memnull[]=$d;
		}
                $cache->store($clients_memnull,$cache_key);
            }else{
                $clients_memnull=$this->dbconn->error;
            }
        }
	$sql_mem2G="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_mem2G.total,0) as total from compat_rf left join target_mem2G using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_2G';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_2G=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'mem2G');
            $result=$this->dbconn->query($sql_mem2G);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_2G=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_2G[]=$d;
		}
                $cache->store($clients_2G,$cache_key);
            }else{
                $clients_2G=$this->dbconn->error;
            }
        }
	$sql_mem4G="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_mem4G.total,0) as total from compat_rf left join target_mem4G using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_4G';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_4G=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'mem4G');
            $result=$this->dbconn->query($sql_mem4G);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_4G=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
                    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_4G[]=$d;
		}
                $cache->store($clients_4G,$cache_key);
            }else{
                $clients_4G=$this->dbconn->error;
            }
        }
	$sql_mem8G="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_mem8G.total,0) as total from compat_rf left join target_mem8G using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_8G';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_8G=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'mem8G');
            $result=$this->dbconn->query($sql_mem8G);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_8G=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
                    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_8G[]=$d;
		}
                $cache->store($clients_8G,$cache_key);
            }else{
                $clients_8G=$this->dbconn->error;
            }
        }
        // cpu
	$sql_cpunull="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_cpunull.total,0) as total from compat_rf left join target_cpunull using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_cpunull';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_cpunull=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'cpunull');
            $result=$this->dbconn->query($sql_cpunull);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_cpunull=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_cpunull[]=$d;
		}
                $cache->store($clients_cpunull,$cache_key);
            }else{
                $clients_mono=$this->dbconn->error;
            }
        }
	$sql_cpu_mono="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_cpu_mono.total,0) as total from compat_rf left join target_cpu_mono using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_cpu_mono';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_mono=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'cpu_mono');
            $result=$this->dbconn->query($sql_cpu_mono);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_mono=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_mono[]=$d;
		}
                $cache->store($clients_mono,$cache_key);
            }else{
                $clients_mono=$this->dbconn->error;
            }
        }
	$sql_cpu_dual="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_cpu_dual.total,0) as total from compat_rf left join target_cpu_dual using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_cpu_dualquad';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_dualquad=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'cpu_dual');
            $result=$this->dbconn->query($sql_cpu_dual);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_dualquad=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_dualquad[]=$d;
		}
                $cache->store($clients_dualquad,$cache_key);
            }else{
                $clients_dualquad=$this->dbconn->error;
            }
        }
	$sql_cpu_other="select compat_rf.year,compat_rf.month,compat_rf.rel,compat_rf.fla,ifnull(target_cpu_more.total,0) as total from compat_rf left join target_cpu_more using(year,month,rel,fla) order by year desc,month desc,compat_rf.rel asc,compat_rf.fla asc";
        $cache_key='extended_memory_cpu_other';
        $data = $cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $clients_more=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'cpu_more');
            $result=$this->dbconn->query($sql_cpu_other);
            if ($result){
                $this->times+=microtime(true)-$stime;
                $clients_more=[];
		$tmp=[];
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
		    $date=$row['year'].'_'.$row['month'];
                    $tmp[$date][$row['rel']][$row['fla']]=intval($row['total']);
                }
		foreach($tmp as $d){
			$clients_more[]=$d;
		}
                $cache->store($clients_more,$cache_key);
            }else{
                $clients_more=$this->dbconn->error;
            }
        }

	//ltsp
	$sql_ltsp_types="select compat_t.year,compat_t.month,compat_t.type,ifnull(target_type.total,0) as total from compat_t left join target_type using(year,month,type) order by year desc,month desc,compat_t.type asc";
        $count_ltsp=array();
        $cache_key='ltsp_types';
        $data=$cache->get($cache_key);
        $stime=microtime(true);
        if ($data != false){
            $count_ltsp=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'ltsp_type');
	    $result=$this->dbconn->query($sql_ltsp_types);
            if ($result){
                $this->times+=microtime(true)-$stime;
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
                    if (isset($row['type']) and $row['type'] != NULL){
                        $count_ltsp[]=array(strtolower($row['type']),$row['total']);
                    }
                }
                $cache->store($count_ltsp,$cache_key);
            }else{
                $count_ltsp=$this->dbconn->error;
            }
        }
        $cache_key='ltsp_modes';
	$sql_ltsp_modes="select compat_m.year,compat_m.month,compat_m.mode,ifnull(target_mode.total,0) as total from compat_m left join target_mode using(year,month,mode) order by year desc,month desc,compat_m.mode asc";
	$data= $cache->get($cache_key);
        $stime=microtime(true);
        $count_mode=array();
        if ($data != false){
            $count_mode=$data;
        }else{
	    $this->execute_sql_array($sql_targets,'ltsp_mode');
	    $result=$this->dbconn->query($sql_ltsp_modes);
            if ($result){
                $this->times+=microtime(true)-$stime;
                while($row=$result->fetch_array(MYSQLI_ASSOC)){
                    if (isset($row['mode']) and $row['mode'] != NULL){
                        $count_mode[]=array(strtolower($row['mode']),$row['total']);
                    }
                }
                $cache->store($count_mode,$cache_key);
            }else{
                $count_mode=$this->dbconn->error;
            }
        }

         //sanitize input
        if ($app != NULL){
             $app=preg_grep('/^[a-zA-Z0-9\-_]+$/',array($app));
             if ($app != NULL and isset($app[0])){
                 $app=$this->dbconn->real_escape_string($app[0]);
                 $stats['apps']=[];
                 $sql="select year,month,rel,fla,string,ifnull(count,0) as count from compat_rf join (select distinct string from RecvPackages where string like '$app%')compat_rfapp left join (select year(date) as year,month(date) as month,string,Releases_name as rel,Flavours_name as fla,sum(count) as count from RecvPackages where string like '$app%' and date >= date_sub(now(),interval 1 year) group by year,month,string,Releases_name,Flavours_name)a using(year,month,rel,fla,string) order by compat_rfapp.string,year desc,month desc";
                    $cache_key="extended_app_$app";
                    $data = $cache->get($cache_key);
                    $stime=microtime(true);
                    if ($data != false){
                        $stats['apps']=$data;
                    }else{
                        $result=$this->dbconn->query($sql);
                        if ($result){
                         $this->times+=microtime(true)-$stime;
                         $tmp=[];
                         while($row=$result->fetch_array(MYSQLI_ASSOC)){
                             $date=$row['year'].'_'.$row['month'];
                             $tmp[$row['string']][$date][$row['rel']][$row['fla']]=intval($row['count']);
                         }
                    foreach ($tmp as $app_string => $values){
                    
                        $app_use=[];
                        foreach($values as $date => $reldata){
                            $app_use[]=$reldata;
                        }
                        $stats['apps'][]=array('app'=>$app_string, 'app_use'=> $app_use);
                    }
                       
                        //    $cache->store($tmp2,$cache_key);
                         
                     }else{
                         $app_use=$this->dbconn->error;
                     }
                 }
             }
         }
         // FINALIZATION & WRITE STRUCTURE
         if (isset($clients_month)){
             $stats['clients']['clients_per_month']=$clients_month;
         }
         if (isset($machines_month)){
            $stats['clients']['machines_per_month']=$machines_month;
         }
         if (isset($num_updates_month)){
             $stats['clients']['freq_updates_per_month']=$num_updates_month;
         }
	 if (isset($change_releases)){
             $stats['clients']['change_releases']=$change_releases;
         }
         if (isset($change_flavour)){
             $stats['clients']['change_flavours']=$change_flavour;
	 }
         if (isset($clients_arch)){
             $stats['clients']['architectures']=$clients_arch;
         }
	if (isset($clients_memnull)){
             $stats['clients']['mem']['unkn']=$clients_memnull;
         }
         if (isset($clients_2G)){
             $stats['clients']['mem']['2G']=$clients_2G;
         }
         if (isset($clients_4G)){
             $stats['clients']['mem']['4G']=$clients_4G;
         }
         if (isset($clients_8G)){
             $stats['clients']['mem']['8G']=$clients_8G;
         }
         if (isset($clients_cpunull)){
             $stats['clients']['cpu']['unkn']=$clients_cpunull;
         }
         if (isset($clients_mono)){
             $stats['clients']['cpu']['mono']=$clients_mono;
         }
         if (isset($clients_dualquad)){
             $stats['clients']['cpu']['dualquad']=$clients_dualquad;
         }
         if (isset($clients_more)){
             $stats['clients']['cpu']['more']=$clients_more;
         }
         if (isset($count_ltsp)){
             $stats['clients']['count_ltsp']=$count_ltsp;
         }
         if (isset($count_mode)){
             $stats['clients']['count_mode']=$count_mode;
         }
         $stats['debug_query_time']=strval(number_format($this->times,5));
         if (file_exists($this->ka_file)){
             $stats['debug_keep_alive']=date('Y-m-d H:i',file_get_contents($this->ka_file));
         }
         if (isset($this->swversion)){
            $stats['debug_swversion']=$this->swversion;
         }
         return json_encode($stats);
     }

     function get_historic_data($typechart='',$param=NULL){
         $this->load_alias();
         $obj=[];
         $this->times=0;
         foreach ($this->info_distro['distros'] as $distro){
             $dname=$distro['name'];
             $dlike=$distro['like'];
             $obj[$dname]=array();
             foreach ($distro['sabor'] as $sabor){
                 $sname=$sabor['name'];
                 $slike=$sabor['like'];
                 $obj[$dname][$sname][]=$this->get_chart($dlike,$slike,'current',$typechart,$param);
                 if ($param == NULL){
                     $obj[$dname][$sname][]=$this->get_chart($dlike,$slike,'old',$typechart);
                     $obj[$dname][$sname][]=$this->get_chart($dlike,$slike,'very_old',$typechart);
                }
             }
         }
         $obj['debug_query_time']=strval(number_format($this->times,3));
         if (array_key_exists('init_range',$this->dates)){
            $obj['debug_init_range']=strval($this->dates['init_range']);
         }
         if (array_key_exists('end_range',$this->dates)){
            $obj['debug_end_range']=strval($this->dates['end_range']);
         }
         if (file_exists($this->ka_file)){
             $obj['debug_keep_alive']=date('Y-m-d H:i',file_get_contents($this->ka_file));
         }
         if (isset($this->swversion)){
            $obj['debug_swversion']=$this->swversion;
         }
         return json_encode($obj);
     }

    function get_chart($version='',$sabor='',$type='current',$typechart='',$param=NULL){
        if ($typechart == ''){
            $cache_key="$version"."_"."$sabor"."_"."$type";
            $limit = "limit 10";
            $sql_limit=10;
            $and = "";
        }else{
            $cache_key="$version"."_"."$sabor"."_"."$type"."_"."$typechart";
            $limit = "";
            $sql_limit=1000;
            $and = "and string in ( select `name` from `PackagesWhitelist` where status = '1' )";
        }
        if ($version != ''){
            $version = " and Releases_name = '$version' ";
        }
        if ($sabor != ''){
            $sabor = " and Flavours_name = '$sabor' ";
        }
        $order=" order by count desc $limit ";
        $group=" group by app ";

        if ($param == NULL){
            $where=$this->dates['date_'.$type]." $version $sabor ";
            $where_clients=$this->dates['date_'.$type]." $version $sabor ";
        }else{
            $this->init_dates($param);
            $cache_key.='_'.$this->dates['init_range'].'_'.$this->dates['end_range'];
            $where=$this->dates['custom_range']." $version $sabor ";
            $where_clients=$this->dates['custom_range']." $version $sabor ";
        }

        $sql="SELECT string as app,sum(count) as count from RecvPackages where $where $and $group $order";
        $sql_clients = "select count(distinct Client_uid) as count from Client_Versions where $where_clients $order";
        $cache = new Cache;
        $data = $cache->get($cache_key);
        if ($data != false){
            return $data;
        }else{
            $data=array($this->get_result_from_sql($sql,$sql_limit),$this->get_clients_from_sql($sql_clients));
            $cache->store($data,$cache_key);
            return $data;
        }
     }
     function get_clients_from_sql($sql){
             $stime=microtime(true);
         if ($result=$this->dbconn->query($sql)){
                 $etime=microtime(true);
                 $this->times+=($etime-$stime);
             while($row=$result->fetch_array(MYSQLI_ASSOC)){
                 if (isset($row['count'])){
                     return array('nclients'=>$row['count']);
                 }
             }
             return array('nclients'=>'not available');
         }else{
             return array('nclients'=>$this->dbconn->error);
         }

     }
     function get_result_from_sql($sql,$limit){
             $stime=microtime(true);
         if ($result=$this->dbconn->query($sql)){
                 $etime=microtime(true);
                 $this->times+=($etime-$stime);
             $obj2=[];
             $nobj=0;
             while($row=$result->fetch_array(MYSQLI_ASSOC)){
                 if (array_key_exists($row['app'],$this->alias)){
                     if (! empty($this->alias[$row['app']])){
                         if ($nobj < $limit)
                             $obj2[$this->alias[$row['app']]]=$row['count'];
                         $nobj++;
                     }
                 }else{
                     if ($nobj < $limit)
                         $obj2[$row['app']]=$row['count'];
                     $nobj++;
                 }
             }
             return $obj2;
         }else{
             return $this->dbconn->error;
         }
     }
     function purge_whitelist($data){
        $purged = array();
        if (count($data) == 0){
            return $purged;
        }
        $mode = NULL;
        if (array_key_exists('string',$data[0])){
            $mode = 'string';

        }
        if (array_key_exists('name',$data[0])){
            $mode = 'name';
        }
        if ($mode == NULL){
            return $purged;
        }
        foreach ($data as $item){
            $i = strtolower($item[$mode]);
            if (preg_match('/^[a-z0-9][a-z0-9_.+\-]+$/',$i)){
                if (preg_match('/[.](png|zip|jpg|php|txt|desktop|sql|sb2|ts|bz2|docbook|mo|iso|json|swf|xcf|md|egg-info|skm|js|html|bmp|svg|install|zero|dll|so|app|exe|gif|doc|cpp|h|css|java|xsl|xml|ui|ko|notebook|ogg|mp3|mp4|avi|mpg|c|pdf|o|ps|a|gz|bz|ini)$/',$i)){
                    $i = NULL;
                }else{
                    if (preg_match('/^(smart_|xvf|drivelist|geany_run)/',$i)){
                        $i = NULL;
                    }
                }
            }else{
                $i = NULL;
            }
            if ($i != NULL){
                if ($mode == 'string'){
                    $purged[]=array($mode=>$i);
                }else{
                    $purged[]=array($mode=>$i,'status'=>$item['status']);
                }
            }
        }
        return $purged;
     }
    function get_whitelist_form(){
        $cache = new Cache();
        $cache_key = 'whitelist';
        $data = $cache->get($cache_key);
        if ($data != false){
            return $data;
        }
        $sql = "select distinct `string` from `RecvPackages` order by `string` asc";
        $sql2 = "select `name`,`status` from `PackagesWhitelist`";
        $result=$this->dbconn->query($sql);
        $all_items=array();
        if ($result){
            while($row=$result->fetch_array(MYSQLI_ASSOC)){
                $all_items[]=$row;
            }
            if (count($all_items) > 10000){
                $all_items = $this->purge_whitelist($all_items);
            }
        }
        $whitelist=array();
        $result = $this->dbconn->query($sql2);
        if ($result){
            while($row=$result->fetch_array(MYSQLI_ASSOC)){
                $whitelist[] = $row;
            }
            if (count($whitelist) > 10000){
                $whitelist = $this->purge_whitelist($whitelist);
            }
        }
        if (count($all_items) == 0){
            return false;
        }
        $classify = ['in'=> array(), 'out'=>array(), 'unk' => array()];
        $clasified = array();
        foreach ($whitelist as $tmp){
            if ($tmp['status'] == '0'){
                $classify['out'][]=$tmp['name'];
                $clasified[] = $tmp['name'];
            }else if($tmp['status'] == '1'){
                $classify['in'][]=$tmp['name'];
                $clasified[] = $tmp['name'];
            }
        }
        foreach ($all_items as $tmp){
            if (! in_array($tmp['string'],$clasified)){
                $classify['unk'][] = $tmp['string']; 
            }
        }
        $cache->store($classify,$cache_key);
        return $classify;
    }
} 

?>
