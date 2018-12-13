<?php

require_once __DIR__ . '/vendor/autoload.php';
require_once('db.php');
require_once('config.php');
require_once('functions.php');

#error_reporting(E_ALL);
#ini_set('display_errors','on');

$klein = new \Klein\Klein();
$request = \Klein\Request::createFromGlobals();

$klein->respond('GET','/ShowStats',call_show_stats());
$klein->respond('GET','/GetStats',call_get_stats());
$klein->respond('GET','/ShowExtendedStats',call_show_extended_stats());
$klein->respond('GET','/GetExtendedStats',call_get_extended_stats());
$klein->respond('GET','/GetLliurexStats',call_get_lliurex_stats());
$klein->respond('GET','/ShowLliurexStats',call_show_lliurex_stats());
$klein->respond('GET','/SystemStats',call_get_system_stats());
$klein->respond('GET','/ShowSystemStats',call_show_system_stats());
$klein->respond('GET','/getlist',call_getlist());
$klein->respond('GET','/ConfigureWhitelist',call_configure_whitelist());
$klein->respond('POST','/PutWhitelist',modify_whitelist());
$klein->respond('GET','/GetWhitelistItems',get_whitelist_data());
$klein->respond('POST','/notify',call_bd());


define('APP_PATH', $app_dir);
$path=substr($request->server()->get('REQUEST_URI'), strlen(APP_PATH));
$request->server()->set('REQUEST_URI',$path);
$klein->dispatch($request);
?>