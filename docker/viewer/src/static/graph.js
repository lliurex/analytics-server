function drawChart(datos,title,id,nelements) {
  var custom_width=$('#'+id).parent().width()*0.95;
//  if (nelements < 10){
//    var custom_height=$(window).height()/3*0.75;
//  }else{
    var custom_height=20*nelements;
//  }

  // Set chart options
//chartArea:{left:'10%',right:'5%'},
  var options = {title:title,
                 width: custom_width,
                 height: custom_height,
                 fontSize: 10,
                 legend: 'none',
                 hAxis: {
                    viewWindow:{
                        min:0
                    }
                 },
        chartArea:{left:'10%',right:'5%',top:'50',width:'100%',height:'100%'},
        backgroundColor: 'transparent',
                };


  // Instantiate and draw our chart, passing in some options.
  var view = new google.visualization.DataView(datos);
  view.setColumns([0, 1,
                       { calc: "stringify",
                         sourceColumn: 1,
                         type: "string",
                         role: "annotation" }]);
  var chart = new google.visualization.BarChart(document.getElementById(id));
  google.visualization.events.addListener(chart, 'ready', ready_charts);
  chart.draw(view, options);
}

function get_sizes(id){
    var custom_width=$('#'+id).parent().width()*0.95;
    var custom_height=$(window).height()*0.72/2;
    //custom_width='auto';
    custom_height='auto';
    switch(id){
        case 'clients_per_month':
        case 'freq_updates_per_month':
        case 'change_releases':
        case 'change_flavours':
            break;
        case 'architectures':
        case 'mem':
        case 'cpu':
            break
    }
    return {'width':custom_width,'height':custom_height};
}

function hslToHex(h, s, l) {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = n => {
      const k = (n + h / 30) % 12;
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
      return Math.round(255 * color).toString(16).padStart(2, '0');   // convert to Hex and prefix "0" if needed
    };
    return `#${f(0)}${f(8)}${f(4)}`;
}

function GetColors (amount) {
    let saturation = 100
    let lightness = 50
    // let alpha = 1.0
    let colors = []
    let huedelta = Math.trunc(360 / amount)

    for (let i = 0; i < amount; i++) {
        let hue = i * huedelta
        colors.push(hslToHex(hue,saturation,lightness))
        //colors.push(`hsla(${hue},${saturation}%,${lightness}%,${alpha})`)
    }
    return colors
}

const isObject = (obj) => {
    return Object.prototype.toString.call(obj) === '[object Object]'
}

function build_data_per_month(type,resume,data,title){
    let grouptitles = {}
    let keys = {}
    let date_values = []
    let dates_axis = []
    let d = new Date()
    let all_colours = []
    for (const [monthidx,datamonth] of Object.entries(data)){
        nmonthidx = parseInt(monthidx)
        let targetdate
        if (nmonthidx != 0){
            targetdate = new Date(d.getFullYear(),d.getMonth()-nmonthidx+1,1)
            targetdate.setDate(targetdate.getDate()-1)
        }else{
            targetdate = new Date(d.getFullYear(),d.getMonth(),d.getDate())
        }
        
        dates_axis.push(targetdate)
        let totalmonthdata = {}
        loop:
        for (const [rel,reldata] of Object.entries(datamonth)){
            totalmonthdata = totalmonthdata || {}
            let lreldata = Object.entries(reldata)
            if (lreldata.length == 0){
                totalmonthdata[monthidx] = datamonth
                grouptitles = datamonth
                break loop
            } 
            for (const [fla,fladata] of lreldata){
                let groupby
                if (type=='releases'){
                    groupby = rel
                    grouptitles[rel] = true
                }else{
                    groupby = fla
                    grouptitles[fla] = true
                }
                if (isObject(fladata)){
                    for (const [key,keydata] of Object.entries(fladata)){
                        let allkey = 'all_' + key
                        keys[key] = true
                        totalmonthdata[allkey] = totalmonthdata[allkey] || 0
                        totalmonthdata[groupby] = totalmonthdata[groupby] || {}
                        totalmonthdata[groupby][key] = totalmonthdata[groupby][key] || 0
                        totalmonthdata[groupby].all = totalmonthdata[groupby].all || 0
                        totalmonthdata[groupby][key] += keydata
                        totalmonthdata[groupby].all += keydata
                        totalmonthdata[allkey] += keydata
                    }
                }else{
                    totalmonthdata.all = totalmonthdata.all || 0
                    totalmonthdata[groupby] = totalmonthdata[groupby] || 0
                    totalmonthdata[groupby] += fladata
                    totalmonthdata.all += fladata
                }
            }
        }
        let i = 0
        if (resume == false){
            let nrel = Object.keys(grouptitles).length
            let nkey = Object.keys(keys).length
            if (nkey == 0){
                nkey = 1
            }
            if (all_colours.length == 0) all_colours = GetColors(nrel*nkey)
        }else{
            let nkey = Object.keys(keys).length
            if (all_colours.length == 0) all_colours = GetColors(nkey)
        }
        let datatuple = [targetdate]
        for (const [rel,count] of Object.entries(totalmonthdata).sort()){
            if (! resume && rel.startsWith('all')) continue
            if (resume && ! rel.startsWith('all')) continue
            if (isObject(count)){
                for (const [key,keyval] of Object.entries(totalmonthdata[rel]).sort()){
                    if (! resume && key.startsWith('all')) continue
                    if (resume && ! key.startsWith('all')) continue
                    datatuple.push(keyval)
                    datatuple.push(all_colours[i])
                    i++
                }
            }else{
                datatuple.push(count)
                datatuple.push(all_colours[i])
                i++
            }
        }
        date_values.push(datatuple)
    }
    let data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Release')
    let header_group
    if (resume){
        header_group = keys
    }else{
        header_group = grouptitles
    }
    for (const grouptitle of Object.keys(header_group).sort()){
        if (!resume && Object.keys(keys).length != 0){
            for (const keyname of Object.keys(keys).sort()){
                let title = grouptitle+' '+keyname
                data_table.addColumn('number','Total '+title)
                data_table.addColumn({type:'string',role:'style'},'Style '+title)
            }
        }else{
            data_table.addColumn('number','Total '+grouptitle)
            data_table.addColumn({type:'string',role:'style'},'Style '+grouptitle)
        }
    }
    data_table.addRows(date_values)
    let options= {  title: title, 
        curveType: 'function', 
        isStacked: false,
        hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
        vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
        legend:{textStyle:{fontSize: 10}},
        chartArea:{left:'5%',right:'10%'},
        focusTarget: 'category',
        colors: all_colours,
        lineWidth: 5,
        tooltip: { textStyle: { fontSize: 10 } },
        backgroundColor: 'transparent',
        };
    return {data:data_table,options:options}
}

function build_data_from_array(data,title){
    let dates_axis = []
    let d = new Date()
    let data_table = new google.visualization.DataTable()
    data_table.addColumn({type:'date',role:'domain'},'Nhosts')
    data_table.addColumn('number',title)
    let date_values=[]
    for (let i=0;i<data.length;i++){
        let month=d.getMonth()
        let year=d.getFullYear()
        let date_to_add
        if (i==0){
            date_to_add = new Date(d)
        }else{
            date_to_add = new Date(year,month,1)
            date_to_add.setDate(date_to_add.getDate()-1)
            d.setMonth(month-1)
        }
        dates_axis.push(date_to_add)
        date_values.push([date_to_add,data[i]])
    }
    data_table.addRows(date_values)
    let options= {  title: title,
                    curveType: 'function',
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num hosts',minValue: 0,maxValue:'automatic',viewWindowMode:'pretty',viewWindow:{min:0,max:'auto'},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    lineWidth: 5,
                    tooltip: { textStyle: { fontSize: 10 } },
                    backgroundColor: 'transparent',
                };
    return {data:data_table,options:options}
}
function doExtendedChart(){
    end_load_time=get_time();
    var parameter=window.location.search.substr(1);
    if (parameter != ''){
        parameter='?'+parameter;
    }
    var chart_data={};
    start_get_time=get_time();
    $('#accordion').append('<div id="loading"></div>');
    end_get_time=0;
    start_graph_time=0;
    function success ( json ) {
        // json = JSON.parse(json);
        end_get_time=get_time();
        start_graph_time=end_get_time;
        var app=null;
        var order = {'machines_per_month':{},'clients_per_month':{},'freq_updates_per_month':{},'change_releases':{},'change_flavours':{},'count_ltsp':{},'count_mode':{},'architectures':{},'mem':{},'cpu':{}}
        for (var key in json){
        if (key == 'clients'){
            for (var type in order){
                if (! json[key][type]){
                    continue;
                }
                switch(type){
                    case 'machines_per_month':
                        if (! chart_data['clients_per_month']){
                            chart_data['clients_per_month']={};
                        }
                        if (! chart_data['clients_per_month']['hosts']){
                            chart_data['clients_per_month']['hosts']={};
                        }
                        chart_data['clients_per_month']['title']='Machines';
                        chart_data['clients_per_month']['hosts']['graph']=build_data_from_array(json[key][type],'Number of unique machines used')
                        chart_data['clients_per_month']['hosts']['title']='Number of unique machines used';
                        break;
                    case 'clients_per_month':
                        if (! chart_data['clients_per_month']){
                            chart_data['clients_per_month']={};
                        }
                        if (! chart_data['clients_per_month']['releases']){
                            chart_data['clients_per_month']['releases']={};
                        }
                        if (! chart_data['clients_per_month']['flavours']){
                            chart_data['clients_per_month']['flavours']={};
                        }
                        chart_data[type]['title']='Machines';
                        chart_data[type]['releases']['graph']=build_data_per_month('releases',false,json[key][type],'Number instances by release per month')
                        chart_data[type]['releases']['title']='Number instances by release per month';
                        chart_data[type]['flavours']['graph']=build_data_per_month('flavours',false,json[key][type],'Number instances by flavour per month')
                        chart_data[type]['flavours']['title']='Number instances by flavour per month';
                        break;
                    case 'freq_updates_per_month':
                if (! chart_data['changes']){
                            chart_data['changes']={};
                            chart_data['changes']['title']='Upgrades';
                        }
                if (! chart_data['changes']['updates']){
                    chart_data['changes']['updates']={};
                }
                        chart_data['changes']['updates']['graph']=build_data_from_array(json[key][type],'Number updates per month')
                        chart_data['changes']['updates']['title']='Number updates per month';
                        break;
                    case 'change_releases':
                        if (! chart_data['changes']){
                            chart_data['changes']={};
                            chart_data['changes']['title']='Upgrades';
                        }
                        if (! chart_data['changes']['releases'])
                            chart_data['changes']['releases']={};
                        chart_data['changes']['releases']['graph']=build_data_from_array(json[key][type],'Change releases per month')
                        chart_data['changes']['releases']['title']='Change releases per month';
                        break;
                    case 'change_flavours':
                        if (! chart_data['changes']){
                            chart_data['changes']={};
                            chart_data['changes']['title']='Changes';
                        }
                        if (! chart_data['changes']['flavours'])
                            chart_data['changes']['flavours']={};
                        chart_data['changes']['flavours']['graph']=build_data_from_array(json[key][type],'Change flavours per month')
                        chart_data['changes']['flavours']['title']='Change flavours per month';
                        break;
                    case 'architectures':
                        if (! chart_data[type]){
                            chart_data[type]={'global':{},'releases':{},'flavours':{}}
                            chart_data[type]['title']='Architectures';
                        }
                        chart_data[type]['global']['graph']=build_data_per_month('flavours',true,json[key][type],'Architectures per month');
                        chart_data[type]['global']['title']='Architectures distribution per month'
                        chart_data[type]['releases']['graph']=build_data_per_month('releases',false,json[key][type],'Architectures by release per month');
                        chart_data[type]['releases']['title']='Architectures distribution by release per month'
                        chart_data[type]['flavours']['graph']=build_data_per_month('flavours',false,json[key][type],'Architectures by flavour per month');
                        chart_data[type]['flavours']['title']='Architectures distribution by flavour per month'
                        break;
                    case 'mem':
                        if (! chart_data[type]){
                            chart_data[type]={'global':{},'releases':{},'flavours':{}};
                            chart_data[type]['title']='Memory';
                        }
                        chart_data[type]['global']['graph']=build_data_per_month('flavours',true,json[key][type],'Memory per month');
                        chart_data[type]['global']['title']='Memory distribution per month'
                        chart_data[type]['releases']['graph']=build_data_per_month('releases',false,json[key][type],'Memory by release per month');
                        chart_data[type]['releases']['title']='Memory distribution by release per month'
                        chart_data[type]['flavours']['graph']=build_data_per_month('flavours',false,json[key][type],'Memory by flavour per month');
                        chart_data[type]['flavours']['title']='Memory distribution by flavour per month'
                        break;
                    case 'cpu':
                        if (! chart_data['cpu']){
                            chart_data['cpu']={'global':{},'releases':{},'flavours':{}};
                            chart_data['cpu']['title']='CpuS';
                        }
                        chart_data['cpu']['global']['graph']=build_data_per_month('flavours',true,json[key][type],'Number CpuS per month');
                        chart_data['cpu']['global']['title']='Number CpuS distribution per month'
                        chart_data['cpu']['releases']['graph']=build_data_per_month('releases',false,json[key][type],'Number CpuS by release per month');
                        chart_data['cpu']['releases']['title']='Number CpuS distribution by release per month'
                        chart_data['cpu']['flavours']['graph']=build_data_per_month('flavours',false,json[key][type],'Number CpuS by release per month');
                        chart_data['cpu']['flavours']['title']='Number CpuS distribution by flavour per month'
                        break;
                    case 'count_ltsp':
                    case 'count_mode':
                        if (! chart_data['ltsp']){
                            chart_data['ltsp']={}
                            chart_data['ltsp']['title']='LTSP Usage'
                        }
                        if (type == 'count_ltsp'){
                            if (! chart_data['ltsp']['usage']){
                                chart_data['ltsp']['usage']={}
                                chart_data['ltsp']['usage']['graph']=build_data_per_month('releases',false,json[key][type],'LTSP usage per month')
                                chart_data['ltsp']['usage']['title']='LTSP Use'
                            }
                        }
                        if (type == 'count_mode'){
                            if (! chart_data['ltsp']['modes']){
                                chart_data['ltsp']['modes']={}
                                chart_data['ltsp']['modes']['graph']=build_data_per_month('releases',false,json[key][type],'LTSP type by type per month')
                                chart_data['ltsp']['modes']['title']='Clients LTSP Mode'
                            }
                        }
                        break;
                }
            }
        }
        if (key == 'apps'){
            for (var app_num in json['apps']){
                if (json['apps'][app_num]['app']){
                if (json['apps'][app_num]['app_use']){
                    var app=json['apps'][app_num]['app'];
                    var tapp='usage_'+app_num;
                    chart_data[tapp]={};
                        chart_data[tapp]['title']='Application usage '+app;
                        chart_data[tapp]['releases']={};
                        chart_data[tapp]['releases']['graph']=build_data_per_month('releases',false,json[key][app_num]['app_use'],'Application use by release per month ('+app+')');
                        chart_data[tapp]['releases']['title']='Use per month for application '+app;
                        chart_data[tapp]['flavours']={};
                        chart_data[tapp]['flavours']['graph']=build_data_per_month('flavours',false,json[key][app_num]['app_use'],'Application use by flavour per month ('+app+')');
                        chart_data[tapp]['flavours']['title']='Use per month for application '+app;
                }
                
                }
            }
        }
        if (key.startsWith('debug')){
            if (key == 'debug_query_time'){
                query_time=json[key];
            }
            if (key == 'debug_keep_alive'){
                keep_alive=json[key];
            }
        }
        }

        for (var chart_type in chart_data){
        if (! chart_data[chart_type]['title']){
            continue;
        }else{
            $('#accordion').append('<h3 class="'+chart_type+'">'+chart_data[chart_type]['title']+'</h3><div id="'+chart_type+'"></div>');
        }
        for (var chart_variant in chart_data[chart_type]){
            if (chart_variant == 'title'){
                continue;
            }
            if (chart_data[chart_type][chart_variant]['graph']){
                $('#'+chart_type).append('<div id='+chart_type+'_'+chart_variant+'></div>');
                var sizes=get_sizes(chart_type);
                chart_data[chart_type][chart_variant]['graph']['options']['width']=sizes['width'];
                chart_data[chart_type][chart_variant]['graph']['options']['height']=sizes['height'];
                var chart = new google.visualization.LineChart(document.getElementById(chart_type+'_'+chart_variant));
                chart.draw(chart_data[chart_type][chart_variant]['graph']['data'], chart_data[chart_type][chart_variant]['graph']['options']);
            }
        }
        }

        $('#loading').remove();
        $('#accordion').accordion({active:false,collapsible:true,heightStyle: "content",autoHeight:false});
        if (app != null){
        $('.app_use').click();
        }
        end_graph_time=get_time();
        print_stats(end_graph_time,query_time);
        run_css_fixes();
    }
    
    $.ajax({ 	datatype: 'json',
        url: "./GetExtendedStats"+parameter,
        success: success,
        async: true,
    });
    return;
}
function run_css_fixes(){
    $('#accordion>div>div:last-child svg').css('height',String(Number($('#accordion>div>div:last-child svg').css('height').slice(0,-2))*1.1)+'px');
}
function param_to_obj(param){
    if (param.substr(0,1) == '?'){
        param = param.substr(1)
    }
    if (param == ''){
        return 'Undefined'
    }
    var items = {}
    param.split("&").forEach(function(part){
        var i = part.split("=");
        items[i[0]] = decodeURIComponent(i[1]);
    });
    return items;
}
function doChart(typechart=""){
    var parameter=window.location.search.substr(1);
    var tables_per_flavour=3;
    if (parameter != ''){
        parameter='?'+parameter;
        params=param_to_obj(parameter)
        if (!(params.hasOwnProperty('init') && params.hasOwnProperty('window'))){
            parameter = ''
        }else{
            tables_per_flavour=1;
        }
    }
    end_load_time=get_time();
    start_get_time=get_time();

    //Gets Data from DB
    $('#accordion').append('<div id="loading"></div>');
    if (typechart == ''){
        url="./GetStats"+parameter
        limit = 10
    }else{
        url="./GetLliurexStats"+parameter
        limit = 1000
    }
    $.getJSON(url, function( json ) {
        end_get_time=get_time();
        start_graph_time=end_get_time;
        count=0;
        for (key in json){
            if (! key.startsWith('debug')){
                for (key2 in json[key]){
                    count++;
                }
            }
        }
        max_graph=count*tables_per_flavour;
        obj=[];
        var init_range;
        var end_range;
        for (distro in json){
                if (distro == 'debug_init_range'){
                    init_range=json[distro];
                }
                if (distro == 'debug_end_range'){
                    end_range=json[distro];
                }
                if (distro == 'debug_query_time'){
                    query_time=json[distro];
                }
                if (distro == 'debug_keep_alive'){
                    keep_alive=json[distro];
                }
                continue;
        }
        for (distro in json){
            if (distro.startsWith('debug')){
                continue;
            }
            for (sabor in json[distro]){
                var data = json[distro][sabor]
                var all_array = true
                for (var idx=0;idx<data.length;idx++){
                    if (! Array.isArray(data[idx])){
                        all_array = false
                    }
                }
                divname='chart_'+distro+'_'+sabor;
                $('#accordion').append('<h3>Distro '+distro+'('+sabor+')</h3>');
                $('#accordion').append('<div class="'+divname+'"></h3>');
                i = 0
                function makeTable(tabledata,inside){
                    $('div.'+inside).append('<div id="'+divname+i+'"></div>')
                    var k=0
                    var datos=new google.visualization.DataTable()
                    datos.addColumn('string','App')
                    datos.addColumn('number','Count')
                    var app_data = tabledata[0]
                    var client_data = tabledata[1]
                    for (var idxappdata=0; idxappdata < app_data.length; idxappdata++){
                        datos.addRow(app_data[idxappdata])
                        k++
                    }
                    while (k < 10){
                        datos.addRow(['',0])
                        k++
                    }
                    obj.push(datos)
                    titles[i]=titles[i]+' (Total clients: '+client_data['nclients']+')'
                    drawChart(obj[obj.length-1],titles[i],divname+i,k)
                    i++
                }
                if (all_array){
                    tables_per_flavour = data.length
                    titles=['Top apps este mes','Top apps ultimo mes','Top apps penultimo mes'];
                    for (var idx in data){
                        makeTable(data[idx],divname)
                    }
                }else{
                    tables_per_flavour = 1
                    titles=['Top apps from '+init_range+' until '+end_range]
                    makeTable(data,divname)
                }
            }
        }
        end_graph_time=get_time();
        print_stats(end_graph_time,query_time);
        return;
    });
}
num_ready=0;
function ready_charts(){
    num_ready++;
    if (num_ready == max_graph){
        $('#accordion>#loading').remove()
        $('#accordion').accordion({active:false,collapsible:true,heightStyle: "content",autoHeight:false});
        run_css_fixes()
    }
}
function print_stats(gr_time=0,q_time=0){
    var get_time = parseFloat(((end_get_time-start_get_time)/1000)-q_time).toFixed(3)
    var query_time = parseFloat(q_time).toFixed(3)
    if (get_time < 0){
        get_time = parseFloat(query_time) + parseFloat(get_time)
        get_time = get_time.toFixed(3)
        query_time = 0
    }
    var load_time = (end_load_time-start_load_time)/1000
    var graph_time = (gr_time-start_graph_time)/1000
    get_time = get_time.toString()
    if (query_time == 0){
        query_time = query_time.toString()
    }
    load_time = load_time.toString()
    graph_time = graph_time.toString()
    $('#stats_box').append('<span class="stats">Load time: '+load_time+' sec</span>')
    $('#stats_box').append('<span class="stats">Get time: '+get_time+' sec</span>')
    $('#stats_box').append('<span class="stats">Graph time: '+graph_time+' sec</span>')
    $('#stats_box').append('<span class="stats">Query time: '+query_time+' sec</span>')
    //$('#stats_box').append('<span class="stats">Updated: '+keep_alive.toString()+'</span>')
}
function get_time(){
    return (Date.now ? Date.now() : new Date().getTime()) ;
}
var start_graph_time=0;
var end_graph_time=0;
var start_load_time=get_time();
var end_load_time=0;
var start_get_time=0;
var end_get_time=0;
var query_time='';
var keep_alive='';
