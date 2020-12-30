var stats = {};
var graphs = {};
var charts = {};

var timeout = 10;
var minutes = 10;
var max_items = 6 * minutes;
var parent = '#chart_div';
/*
var show = { 
    load : { title : 'Carga', group : false },
    mem_used : { title : 'Memoria usada', group : false },
    paused : { title : 'Pausa', group : false },
    processed : { group : true, title : 'Procesado', members : {
        processed_client: {title: 'Clientes', group : false},
        processed_desktop : {title : 'Desktops', group : false},
        processed_other : { title: 'Others', group : false},
        processed_server : { title: 'Servers', group : false},
    }},
    processing_at : { title: 'SpeedUp', group : false},
    queues: { group: true, title: 'Queues', members: {
        queue_desktop: {title: 'Desktops', group : false},
        queue_other: { title: 'Others', group : false},
        queue_server: { title: 'Servers', group : false},
        queue_client: { title: 'Clients', group : false},
    }},
    select_window : { title: 'Select Window', group: false},
    temp_sizes:  { group: true, title: 'Temp sizes', members:{
        temp_packages_size: { title: 'Packages', group : false},
        temp_clients_size: { title: 'Clients', group : false}
    }}
};
*/
var show = { 
    load : { title : 'Carga', group : false },
    mem_used : { title : 'Memoria usada', group : false },
    queues: { group: true, title: 'Queues', members: {
        queue_desktop: {title: 'Desktops', group : false},
        queue_other: { title: 'Others', group : false},
        queue_server: { title: 'Servers', group : false},
        queue_client: { title: 'Clients', group : false},
    }},
    select_window : { title: 'Select Window', group: false},
    temp_sizes:  { group: true, title: 'Temp sizes', members:{
        temp_packages_size: { title: 'Packages', group : false},
        temp_clients_size: { title: 'Clients', group : false},
    }},
    db_sizes: { group:true,title:'DB sizes',members:{
        db_clients_size: {title: 'Clients',group:false},
        db_packages_size: {title: 'Packages',group:false},
    }},
    processing_at : { title: 'SpeedUp', group : false},
    paused : { title : 'Pausa', group : false },

};


var cfg = { watched: {}, groups: {}, divs: {}};

function get_cfg(obj,from_group=undefined){
    for (var i in obj){
        try{
            if (obj[i].group){
                cfg.groups[i] = {title: obj[i].title ,members: {}};
                cfg.divs[i] = {title:obj[i].title};
                get_cfg(obj[i].members,i);
            }else{
                cfg.watched[i] = { title : obj[i].title };
                if (from_group){
                    cfg.groups[from_group]['members'][i]={title:obj[i].title};
                }else{
                    cfg.divs[i] = {title: obj[i].title};
                }
            }
        }catch(e){};
    }
}
get_cfg(show);

function get_data(callback=undefined){
    $.getJSON("./SystemStats",function(json){
        for (var key in json){
            if (!(key in cfg.watched))
                if (key != 'keepalive')
                    continue;
            var value=json[key];
            if (key in stats){
                if (stats[key].length > max_items -1){
                    stats[key].splice(0,1);
                }
                stats[key].push(value);
            }else{
                stats[key]=[value];
            }
        }
        if (callback){
            callback();
        }
    })
}

function show_data(callback=undefined){
    $('#accordion').empty();
    var str='';
    var sep='';
    for (var parameter in stats) {
        sep = parameter + ' = ';
        for (var index in stats[parameter]){
            str += sep + stats[parameter][index];
            sep = ', ';
        }
        str += '\n';
    }
    $('#accordion').append('<pre>'+str+'</pre>');
    if (callback){
        callback();
    }
}

function init_system_stats(){
    //$('#header').append($('<button onClick=initialize()>PUSH</button>'));

    initialize();
}

function loop(){
    for (var i = 0; i < arguments.length ; i++){
        f=arguments[i];
        f();
        window.setTimeout(function(){ loop(f) },timeout*1000);
    }
}

var initialized = false;
function initialize(){
    //$('body').append("<div id='loading'></div>");
    if (initialized)
        return true;
    initialized = true;
    //get_data(function(){ init_google_data ( function () {make_divs(parent)})})
    get_data(make_divs);
    loop(function(){ 
        get_data(function(){ 
    //        show_data(); 
            init_google_data();
            gen_google_data();
            $('#loading').remove();
            view_google_graphs();
        })
    })
}

function make_divs(callback=undefined){
    $(parent).empty();
    for (var i in cfg.divs){
        $(parent).append($('<div id="chart_'+i+'"> </div>'));
    }
    if (callback){
        callback();
    }
}
// GOOGLE CODE

function timestamp_to_string(timestamp){
    var time=new Date(timestamp * 1000);
    var h=time.getHours();
    var m=time.getMinutes();
    var s=time.getSeconds();
    if (h < 10){
        h = '0'+ h.toString();
    }
    if (m < 10){
        m = '0'+ m.toString();
    }
    if (s < 10){
        s = '0'+ s.toString();
    }
    return h+':'+m+':'+s;
}
function get_current_divs(){
    var names={};
    $(parent+'>div').each(function(){ names[this.id.substring(6)] = {} });
    return names;
}
function init_google_data(callback=undefined){
    for (var parameter in get_current_divs()){
        graphs[parameter] = new google.visualization.DataTable();
        graphs[parameter].addColumn('string','Time');
        if (parameter in cfg.watched){
            graphs[parameter].addColumn('number',cfg.watched[parameter].title);
        }else{
            for (var member in cfg.groups[parameter].members){
                graphs[parameter].addColumn('number',cfg.groups[parameter].members[member].title);
            }
        }
    }
    if (callback){
        callback();
    }
}

function gen_google_data(callback=undefined){
    for (var parameter in get_current_divs()){
        if (parameter in cfg.groups){
            graphs[parameter].addRows(make_google_array(stats.keepalive,cfg.groups[parameter].members));
        }else{
            var o={};
            o[parameter]={};
            graphs[parameter].addRows(make_google_array(stats.keepalive,o));
        }
    }

    if (callback){
        callback();
    }
}

function make_google_array(iterable_time,members){
    var a = [];
    for (var i=0 ; i<iterable_time.length; i++){
        var timestamp=timestamp_to_string(Number(iterable_time[i]));
        var a2= [timestamp];
        for (var member in members){
            a2.push(Number(stats[member][i]));
        }
        a.push(a2);
    }
    return a;
}

function view_google_graphs(){
    var size = 0;
    for (var key in cfg.divs){
        size+=1;
    }
    var header = 10;
    var margin_left = 75;
    var margin_right = 200;
    var properties = { title: '', height: (window.innerHeight - header) / size, legend : true, backgroundColor: 'transparent', chartArea: {left:margin_left,width:window.innerWidth-(margin_left+margin_right)}, fontSize: 10 ,hAxis:{textPosition:'none'},vAxis :{ viewWindow : {min:0}}};
    for (var parameter in graphs){
        if (parameter in cfg.groups){
            properties['isStacked']='absolute';
        }
        properties.title=cfg.divs[parameter].title;
        charts[parameter] = new google.visualization.AreaChart(document.getElementById('chart_'+parameter));
        charts[parameter].draw(graphs[parameter],properties);
    }
}

//$(document).ready(init_system_stats);