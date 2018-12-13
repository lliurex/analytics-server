<?php
require_once __DIR__ . '/vendor/autoload.php';

$loader = new Twig_Loader_Filesystem('templates');
if (! is_dir('/tmp/twig_cache')){
    mkdir('/tmp/twig_cache');
}
$twig = new Twig_Environment($loader, array(
    'cache' => '/tmp/twig_cache',
));


function make_nav(){
    $nav = array();
    $nav[] = array ('caption' => 'Simple Statistics', 'href' => 'ShowStats');
    $nav[] = array ('caption' => 'Extended Statistics', 'href' => 'ShowExtendedStats');
    $nav[] = array ('caption' => 'Lliurex Statistics', 'href' => 'ShowLliurexStats');
    $nav[] = array ('caption' => 'Whitelist Config', 'href' => 'ConfigureWhitelist');
    $nav[] = array ('caption' => 'System Status', 'href' => 'ShowSystemStats');
    return $nav;
}


function pages($page){
    global $twig;

    switch($page){
        case 'show_stats':
            $template = 'index.tpl';
            $csslib = array("ui/jquery-ui","graph");
            $jslib = array("https://www.gstatic.com/charts/loader","jquery.min","graph_min","ui/jquery-ui","query");
            $jscmd = array();
            $jscmd[] = 'google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(doChart);';
            $jscmd[] = '$(document).ready(make_query_box);';
            break;
        case 'show_lliurex_stats':
            $template = 'index.tpl';
            $csslib = array("ui/jquery-ui","graph");
            $jslib = array("https://www.gstatic.com/charts/loader","jquery.min","graph_min","ui/jquery-ui","query");
            $jscmd = array();
            $jscmd[] = 'google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(function(){doChart("whitelist")});';
            $jscmd[] = '$(document).ready(make_query_box);';
            break;
        case 'show_extended_stats':
            $template = 'extended.tpl';
            $csslib = array("ui/jquery-ui","graph");
            $jslib = array("https://www.gstatic.com/charts/loader","jquery.min","graph_min","ui/jquery-ui","query");
            $jscmd = array();
            $jscmd[] = 'google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(doExtendedChart);';
            $jscmd[] = '$(document).ready(function(){function send_query(){window.location.href=window.location.pathname+"?app="+$("#query_box>input").val()};$("#query_box>input").on("keyup",function(e){if (e.keyCode == 13) {send_query()}});$("#query_box>button").click(send_query)});';
            break;
        case 'show_system_stats':
            $template = 'sysstats.tpl';
            $csslib = array("graph");
            $jslib = array("https://www.gstatic.com/charts/loader","jquery.min","sysstats");
            $jscmd = array('google.charts.load("current", {packages: ["corechart"],"language":"es"}); google.charts.setOnLoadCallback(initialize);');
            break;
        case 'show_whitelist':
            $template = 'whitelist.tpl';
            $csslib = array("whitelist","graph");
            $jslib = array("jquery.min","whitelist");
            $jscmd = array('$(document).ready(start);');
            break;
    };

    return function($request,$response,$service) use(&$twig,$template,$csslib,$jslib,$jscmd){
        echo $twig->render($template, array('csslib' => $csslib , 'jslib' => $jslib , 'jscmd' => $jscmd ,'navigation' => make_nav()));
    };
}

?>