<?php 
function call_bd(){
	return function($request,$response,$service){
		$data=json_decode($request->stats,true);
		
		$db = new DB;
		$db->connect();
		try{
			if (isset($data['vers'])){
			    $version=trim($data['vers']);
			}else{
			    return 'NOK';
			}
			if (isset($data['sab'])){
			    $sabor=trim($data['sab']);
			}else{
			    return 'NOK';
			}
			if (isset($data['uid'])){
			    $uid=trim($data['uid']);
			}else{
			    return 'NOK';
			}
			if ($version == '' or $sabor == '' or $uid == ''){
			    return 'NOK';
			}
			if (isset($data['specs'])){
			    $specs=$data['specs'];
			}else{
			    $specs=false;
			}
			if (isset($data['date'])){
			    $db->send_data($uid,$version,$sabor,json_decode($data['stats'],true),$specs,$data['date']);
			}else{
			    $db->send_data($uid,$version,$sabor,json_decode($data['stats'],true),$specs);
			}
		}catch (Exception $e){
		        //error_log($e);
			$db->disconnect();
			return 'NOK';
		}
		$db->disconnect();
		return 'OK';
	};
}
function modify_whitelist(){
    return function($request,$response,$service){
        $data=$request->status;
        if ($data){
            $data = json_decode($data,true);
        }
        $sql_pre = 'truncate PackagesWhitelist;';
        $sql = 'insert into `PackagesWhitelist` (`name`,`status`) values ';
        $str = '';
        foreach ($data['out'] as $item){
            $str .= "('$item',0),";
        }
        foreach ($data['into'] as $item){
            $str .= "('$item',1),";
        }
//        foreach ($data['unk'] as $item){
//            $str .= "('$item',NULL),";
//        }
        $l=strlen($str);
        if ($l < 1)
            return;
        $str[$l-1]=' ';
        $sql .= $str;
        $sql .= 'on duplicate key update status=VALUES(status);';
        $db = new DB;
        $db->connect();
        try{
            $db->dbconn->query($sql_pre);
            try{
                $db->dbconn->query($sql);
            }catch(Exception $e){
                return 'NOK';
            }
        }catch(Exception $e){
            return 'NOK';
        }
        $db->disconnect();
        $cache = new Cache();
        $cache->invalidate('whitelist');
        return 'OK';
    };
}

function get_whitelist_data(){
	return function($request,$response,$service){
		$db = new DB;
		$db->connect();
                $res=$db->get_whitelist_form();
                $db->disconnect();
                return json_encode($res);
        };
}
function process_window_params($req){
    $p1=$req->param('init');
    $p2=$req->param('window');
    if ($p1 == NULL or $p2 == NULL ){
        return NULL;
    }
    if (! (is_numeric($p1) and is_numeric($p2))){
        return NULL;
    }
    $valid = false;
    for ($i=0;$i<12;$i++){
        $d = date('Yn',strtotime(date('Y-m-01 ').'-'.$i.' month'));
        if ($d == $p1){
            $p2=intval($p2);
            if ($p2 <= $i+1){
                $valid = array('year'=>intval(substr($p1,0,4)),'month'=>intval(substr($p1,4,strlen($p1)-4)),'window'=>intval($p2));
                break;
            }
        }
    }
    return $valid;
}

function call_get_stats(){
	return function($request,$response,$service){
                $param = process_window_params($request);
		$db = new DB;
		$db->connect();
		echo $db->get_historic_data('',$param);
		$db->disconnect();
	};
}

function call_get_lliurex_stats(){
	return function($request,$response,$service){
                $param = process_window_params($request);
		$db = new DB;
		$db->connect();
		echo $db->get_historic_data('whitelist',$param);
		$db->disconnect();
	};
}

function call_get_system_stats(){
    return function($request,$response,$service){
        $db = new DB;
	$db->connect();
	echo $db->get_system_data();
	$db->disconnect();
    };
}

function call_get_extended_stats(){
	return function($request,$response,$service){
	        $app=$request->param('app');
		$db = new DB;
		$db->connect();
		echo $db->get_extended_data($app);
		$db->disconnect();
	};
}

function call_getlist(){
	return function($request,$response,$service){
                $list = array();
                $the_file = 'blacklist.txt';
                if ( !is_file($the_file)) {
                    return json_encode($list);
                }
                try{
                    $content = file_get_contents('blacklist.txt');
                    foreach (explode("\n",$content) as $item){
                        $item = trim($item);
                        if ( $item != '') {
                            $list[] = $item;
                        }
                    }
                }catch(Exception $e){}
                return json_encode($list);
	};
}
require_once 'pages.php';

function call_show_stats(){
    return pages('show_stats');
}
function call_show_lliurex_stats(){
    return pages('show_lliurex_stats');
}
function call_show_system_stats(){
    return pages('show_system_stats');
}
function call_show_extended_stats(){
    return pages('show_extended_stats');
}
function call_configure_whitelist(){
    return pages('show_whitelist');
}
/*
function call_show_stats(){

return function($request,$response,$service){

echo '<html>
  <head>
    <!--Load the AJAX API-->
    <!--<script type="text/javascript" src="https://www.google.com/jsapi"></script>-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript" src="jquery.min.js"></script>
    <script type="text/javascript" src="graph_min.js"></script>

    <script type="text/javascript">
        google.charts.load("current", {packages: ["corechart"],"language":"es"});
        google.charts.setOnLoadCallback(function(){doChart("")});
    </script>
    <script type="text/javascript">
        function send_query_month(){
            var init_selected=$("#init_date_search>option:selected").val();
            var window_selected=$("#date_window_search>option:selected").val();
            window.location.href=window.location.pathname+"?init="+init_selected+"&window="+window_selected;
        }
        function reload_without_params(){
            window.location.href=window.location.pathname;
        }
        function make_month_window(){
            $("#date_window_search").empty()
            var ysel=Number($("#init_date_search>option:selected").val().substr(0,4))
            var msel=Number($("#init_date_search>option:selected").val().substr(4))
            var date=new Date()
            var y = date.getFullYear()
            var m = date.getMonth()+2
            var num = 0
            if (ysel == y){
                num = Math.abs(m - msel)
            }else{
                num = 12 - msel + m
            }
            for (var i=1;i<=num;i++){
                $("#date_window_search").append("<option value=\""+i+"\" name=\""+i+"\">"+i+"</option>");
            }
            $("#query_box>button").unbind("click");
            $("#query_box>button").text("Show");
            $("#query_box>button")[0].disabled = false;
            $("#query_box>button").on("click",send_query_month);
        }
        function make_query_box(){
            var monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic" ];
            var date = new Date();
            var m = date.getMonth();
            var y = date.getFullYear();
            $("#query_box").append("<span>Custom date:");
            $("#query_box").append("Init date<span><select id=\"init_date_search\" name=\"init_date\"><option value=\"\" name=\"\"></option></select></span>");
            $("#query_box").append("Month window<span><select id=\"date_window_search\" name=\"date_window\"></select></span>");
            for (var i=0; i<12; i++){
                var date2 = new Date(y,m,1)
                var strval=date2.getFullYear().toString()+(date2.getMonth()+1).toString();
                var showval=monthNames[m]+"/"+date2.getFullYear().toString()
                $("#init_date_search").append("<option value=\""+strval+"\" name=\""+strval+"\">"+showval+"</option>");
                m--
                if (m < 0){
                    m=11
                    y--
                }
            }
            $("#init_date_search").on("change",make_month_window);
            if (window.location.search != ""){
                $("#query_box").append("<button>Back to normal mode</button>");
                $("#query_box>button").on("click",reload_without_params);
            }else{
                $("#query_box").append("<button disabled>Show range</button>");
            }
        }
        $(document).ready(make_query_box);
    </script>
    <link href="ui/jquery-ui.css" rel="stylesheet">
    <link href="graph.css" rel="stylesheet">
    <link rel="shortcut icon" href="favicon.ico">
    <script type="text/javascript" src="ui/jquery-ui.js"></script>
  </head>
  <body>
  <div id="header"><div id="query_box"></div><span class="title">Lliurex-Analytics <a class="go_to_other" href="ShowExtendedStats">[Extended stats]</a></span><div id="stats_box"></div></div>
  <div id="accordion"></div>
  </body>
</html>
';

};
}


function call_show_lliurex_stats(){

return function($request,$response,$service){

echo '<html>
  <head>
    <!--Load the AJAX API-->
    <!--<script type="text/javascript" src="https://www.google.com/jsapi"></script>-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript" src="jquery.min.js"></script>
    <script type="text/javascript" src="graph_min.js"></script>
    <script type="text/javascript">
        google.charts.load("current", {packages: ["corechart"],"language":"es"});
        google.charts.setOnLoadCallback(function(){doChart("whitelist")});
    </script>
    <script type="text/javascript">
        function send_query_month(){
            var init_selected=$("#init_date_search>option:selected").val();
            var window_selected=$("#date_window_search>option:selected").val();
            window.location.href=window.location.pathname+"?init="+init_selected+"&window="+window_selected;
        }
        function reload_without_params(){
            window.location.href=window.location.pathname;
        }
        function make_month_window(){
            $("#date_window_search").empty()
            var ysel=Number($("#init_date_search>option:selected").val().substr(0,4))
            var msel=Number($("#init_date_search>option:selected").val().substr(4))
            var date=new Date()
            var y = date.getFullYear()
            var m = date.getMonth()+2
            var num = 0
            if (ysel == y){
                num = Math.abs(m - msel)
            }else{
                num = 12 - msel + m
            }
            for (var i=1;i<=num;i++){
                $("#date_window_search").append("<option value=\""+i+"\" name=\""+i+"\">"+i+"</option>");
            }
            $("#query_box>button").unbind("click");
            $("#query_box>button").text("Show");
            $("#query_box>button")[0].disabled = false;
            $("#query_box>button").on("click",send_query_month);
        }
        function make_query_box(){
            var monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic" ];
            var date = new Date();
            var m = date.getMonth();
            var y = date.getFullYear();
            $("#query_box").append("<span>Custom date:");
            $("#query_box").append("Init date<span><select id=\"init_date_search\" name=\"init_date\"><option value=\"\" name=\"\"></option></select></span>");
            $("#query_box").append("Month window<span><select id=\"date_window_search\" name=\"date_window\"></select></span>");
            for (var i=0; i<12; i++){
                var date2 = new Date(y,m,1)
                var strval=date2.getFullYear().toString()+(date2.getMonth()+1).toString();
                var showval=monthNames[m]+"/"+date2.getFullYear().toString()
                $("#init_date_search").append("<option value=\""+strval+"\" name=\""+strval+"\">"+showval+"</option>");
                m--
                if (m < 0){
                    m=11
                    y--
                }
            }
            $("#init_date_search").on("change",make_month_window);
            if (window.location.search != ""){
                $("#query_box").append("<button>Back to normal mode</button>");
                $("#query_box>button").on("click",reload_without_params);
            }else{
                $("#query_box").append("<button disabled>Show range</button>");
            }
        }
        $(document).ready(make_query_box);
    </script>
    <link href="ui/jquery-ui.css" rel="stylesheet">
    <link href="graph.css" rel="stylesheet">
    <script type="text/javascript" src="ui/jquery-ui.js"></script>
  </head>
  <body>
  <div id="header"><div id="query_box"></div><span class="title">Lliurex-Analytics <a class="go_to_other" href="ShowExtendedStats">[Extended stats]</a></span><div id="stats_box"></div></div>
  <div id="accordion"></div>
  </body>
</html>
';

};
}

function call_show_system_stats(){

return function($request,$response,$service){

echo '<html>
  <head>
    <!--Load the AJAX API-->
    <!--<script type="text/javascript" src="https://www.google.com/jsapi"></script>-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript" src="jquery.min.js"></script>
    <script type="text/javascript" src="sysstats_min.js"></script>
    <script type="text/javascript">
        google.charts.load("current", {packages: ["corechart"],"language":"es"});
        google.charts.setOnLoadCallback(initialize);
    </script>
    <link href="ui/jquery-ui.css" rel="stylesheet">
    <link href="graph.css" rel="stylesheet">
    <link rel="shortcut icon" href="favicon.ico">
    <script type="text/javascript" src="ui/jquery-ui.js"></script>
  </head>
  <body>
  <div id="chart_div"></div>
  </body>
</html>
';

};

}


function call_show_extended_stats(){

return function($request,$response,$service){

echo '<html>
  <head>
    <!--Load the AJAX API-->
    <!--<script type="text/javascript" src="https://www.google.com/jsapi"></script>-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript" src="jquery.min.js"></script>
    <script type="text/javascript" src="graph_min.js"></script>

    <script type="text/javascript">
        google.charts.load("current", {packages: ["corechart"],"language":"es"});
        google.charts.setOnLoadCallback(doExtendedChart);
    </script>
    <link href="ui/jquery-ui.css" rel="stylesheet">
    <link href="graph.css" rel="stylesheet">
    <link rel="shortcut icon" href="favicon.ico">
    <script type="text/javascript" src="ui/jquery-ui.js"></script>
    <script type="text/javascript">$(document).ready(function(){function send_query(){window.location.href=window.location.pathname+"?app="+$("#query_box>input").val()};$("#query_box>input").on("keyup",function(e){if (e.keyCode == 13){send_query()}});$("#query_box>button").click(send_query)});</script>
  </head>
  <body>
  <div id="header"><div id="query_box"><span>Search by app:</span><input type="search" name="app_search"></input><button>Search</button></div><span class="title">Lliurex-Analytics <a class="go_to_other" href="ShowStats">[Simple stats]</a></span><div id="stats_box"></div></div>
  <div id="accordion"></div>
  </body>
</html>
';

};

}

function call_configure_whitelist(){

return function($request,$response,$service){

echo "<html>
  <head>
    <!--Load the AJAX API-->
    <script type='text/javascript' src='jquery.min.js'></script>
    <link href='whitelist.css' rel='stylesheet'>
    <link rel='shortcut icon' href='favicon.ico'>
    <script type='text/javascript' src='whitelist_min.js'></script>
    <script type='text/javascript'>$(document).ready(start)</script>
  </head>
  <body>
    <div id='header'><span class='title'>Lliurex-Analytics whitelist configurator</span></div>
    <div id='configure_whitelist'>
        <div id='nonwhitelist'>
            <span>Not in whitelist</span>
            <div id='filternot' class='filter'>Filter:<textarea rows='1'></textarea></div>
            <select name='denied' multiple>
            </select>
        </div>
        <div id='btn_left'>
            <button id='btnleft_to_left'>&lt;&lt;&lt;</button>
            <button id='btnleft_to_center'>&gt;&gt;&gt;</button>
        </div>
        <div id='unknown_state_whitelist'>
            <span>New elements</span>
            <div id='filterunk' class='filter'>Filter:<textarea rows='1'></textarea></div>
            <select name='nonselected' multiple>
            </select>
        </div>
        <div id='btn_right'>
            <button id='btnright_to_right'>&gt;&gt;&gt;</button>
            <button id='btnright_to_center'>&lt;&lt;&lt;</button>
        </div>
        <div id='inwhitelist'>
            <span>In whitelist</span>
            <div id='filterin' class='filter'>Filter:<textarea rows='1'></textarea></div>
            <select name='accepted' multiple>
            </select>
        </div>
    </div>
    <div id='send'>
        <button id='send_btn'>Apply</button>
    </div>
  </body>
</html>
";

};

}
*/

?>
