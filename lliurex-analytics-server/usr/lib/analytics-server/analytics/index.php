<?php
require_once __DIR__ . '/vendor/autoload.php';

$loader = new Twig_Loader_Filesystem('templates');
if (! is_dir('/tmp/twig_cache')){
    mkdir('/tmp/twig_cache');
}
$twig = new Twig_Environment($loader, array(
    'cache' => '/tmp/twig_cache',
));

$nav = array();
$nav[] = array ('caption' => 'Simple Statistics', 'href' => 'ShowStats');
$nav[] = array ('caption' => 'Extended Statistics', 'href' => 'ShowExtendedStats');
$nav[] = array ('caption' => 'Lliurex Statistics', 'href' => 'ShowLliurexStats');
$nav[] = array ('caption' => 'Whitelist Config', 'href' => 'ConfigureWhitelist');
$nav[] = array ('caption' => 'System Status', 'href' => 'ShowSystemStats');

$csslib = array("graph");
$jslib = array();
$jscmd = array();

echo $twig->render('index.tpl', array('csslib' => $csslib , 'jslib' => $jslib , 'jscmd' => $jscmd ,'navigation' => $nav));
?>