<?php
$swversion='@swversion@';
$dbhost='localhost';
$dbname='analytics';
$dbuser='@phpuser@';
$dbpass='@phppass@';

$app_dir='/analytics';

$distros=
'
{
  "distros": [
    {
      "name": "15",
      "like": "15",
      "sabor": [
        {
          "name": "desktop",
          "like": "desktop"
        },
        {
          "name": "server",
          "like": "server"
        },
        {
          "name": "client",
          "like": "client"
        }
      ]
    },
    {
      "name": "16",
      "like": "16",
      "sabor": [
        {
          "name": "desktop",
          "like": "desktop"
        },
        {
          "name": "server",
          "like": "server"
        },
        {
          "name": "client",
          "like": "client"
        }
      ]
    },
    {
      "name": "other",
      "like": "",
      "sabor": [
        {
            "name": "other",
            "like": "other"
        }
      ]
    }
  ]
}
';

function debug_json(){
global $distros;
$a=json_decode($distros,true);
$num_distros=count($a['distros']);
echo '<pre>'.var_export($a,true).'</pre>';
echo '<pre>'.$num_distros." distros\n</pre>";
$i=1;
foreach ($a['distros'] as $distro){
    $nombre=$distro['name'];
    $like=$distro['like'];
    $num_sabores=count($distro['sabor']);
    echo "<pre>Distro $i: nombre=$nombre like=$like con $num_sabores sabores.\n</pre>";
    $k=1;
    foreach ($distro['sabor'] as $sabor){
	$sname=$sabor['name'];
	$slike=$sabor['like'];
	echo "<pre>	Sabor $k: nombre=$sname like=$slike.\n</pre>";
	$k++;
    }
    $i++;
}
}
?>
