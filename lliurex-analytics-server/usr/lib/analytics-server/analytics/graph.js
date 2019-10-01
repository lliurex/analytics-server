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

function build_data_per_month_releases(data,title){
    var total=[];
    for (i=0 ; i < 12; i++){
	total[i]={'15':0,'16':0,'19':0,'all':0};
	if (! data[i]){
	    continue;
	}
        for (rel in data[i]){
            if (rel == '15'){
                for (fla in data[i][rel]){
                    total[i][rel]+=data[i][rel][fla];
                }
            }
            if (rel == '16'){
                for (fla in data[i][rel]){
                    total[i][rel]+=data[i][rel][fla];
                }
            }
            if (rel == '19'){
                for (fla in data[i][rel]){
                    total[i][rel]+=data[i][rel][fla];
                }
            }
        }
        total[i]['all']=total[i]['15']+total[i]['16']+total[i]['19']; 
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Release');
    data_table.addColumn('number','Total Release 15');
    data_table.addColumn({type:'string',role:'style'},'Style Release 15');
    data_table.addColumn('number','Total Release 16');
    data_table.addColumn({type:'string',role:'style'},'Style Release 16');
    data_table.addColumn('number','Total Release 19');
    data_table.addColumn({type:'string',role:'style'},'Style Release 19');
    data_table.addColumn('number','Total ALL Releases');
    data_table.addColumn({type:'string',role:'style'},'Style ALL Releases');
    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['15'],'color:blue',total[i-1]['16'],'color:red',total[i-1]['19'],'color:green',total[i-1]['all'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors:['blue','red','green','grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_flavours(data,title){
    var total=[];
    for (i=0 ; i < 12; i++){
        total[i]={'server':0,'client':0,'desktop':0,'other':0,'all':0};
        if (! data[i]){
            continue;
        }
        for (rel in data[i]){
            for (fla in data[i][rel]){
                total[i][fla]+=data[i][rel][fla];
                total[i]['all']+=data[i][rel][fla];
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Flavour');
    data_table.addColumn('number','Total Server');
    data_table.addColumn({type:'string',role:'style'},'Style Server');
    data_table.addColumn('number','Total Client');
    data_table.addColumn({type:'string',role:'style'},'Style Client');
    data_table.addColumn('number','Total Desktop');
    data_table.addColumn({type:'string',role:'style'},'Style Desktop');
    data_table.addColumn('number','Total Other');
    data_table.addColumn({type:'string',role:'style'},'Style Other');
    data_table.addColumn('number','Total ALL Flavours');
    data_table.addColumn({type:'string',role:'style'},'Style Total ALL Flavours');
    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['server'],'color:purple',total[i-1]['client'],'color:teal',total[i-1]['desktop'],'color:gold',total[i-1]['other'],'color:olive',total[i-1]['all'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['purple','teal','gold','olive','grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_arch(data,title){
    var total=[];
    for (var i=0 ; i < 12; i++){
        total[i]={'i686':0,'x86_64':0,'unkn':0};
        if (! data[i]){
            continue;
        }
        for (var rel in data[i]){
            for (var fla in data[i][rel]){
                for (var arch in data[i][rel][fla]){
                    total[i][arch]+=data[i][rel][fla][arch];
                }
            }
        }

    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total x86');
    data_table.addColumn({type:'string',role:'style'},'Style x86');
    data_table.addColumn('number','Total x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style x86_64');
    data_table.addColumn('number','Total unknown');
    data_table.addColumn({type:'string',role:'style'},'Style unknown');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['i686'],'color:purple',total[i-1]['x86_64'],'color:gold',total[i-1]['unkn'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['purple','gold','grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_release_arch(data,title){
    var total=[];
    for (var i=0 ; i < 12; i++){
        total[i]={'15_i686':0,'15_x86_64':0,'15_unkn':0,'16_i686':0,'16_x86_64':0,'16_unkn':0,'19_i686':0,'19_x86_64':0,'19_unkn':0};
        if (! data[i]){
            continue;
        }
        for (var rel in data[i]){
            for (var fla in data[i][rel]){
                for (var arch in data[i][rel][fla]){
                    total[i][rel+'_'+arch]+=data[i][rel][fla][arch];
                }
            }
        }

    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total 15 x86');
    data_table.addColumn({type:'string',role:'style'},'Style 15 x86');
    data_table.addColumn('number','Total 15 x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style 15 x86_64');
    data_table.addColumn('number','Total 15 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 15 unknown');
    data_table.addColumn('number','Total 16 x86');
    data_table.addColumn({type:'string',role:'style'},'Style 16 x86');
    data_table.addColumn('number','Total 16 x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style 16 x86_64');
    data_table.addColumn('number','Total 16 unkown');
    data_table.addColumn({type:'string',role:'style'},'Style 16 unknown');
    data_table.addColumn('number','Total 19 x86');
    data_table.addColumn({type:'string',role:'style'},'Style 19 x86');
    data_table.addColumn('number','Total 19 x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style 19 x86_64');
    data_table.addColumn('number','Total 19 unkown');
    data_table.addColumn({type:'string',role:'style'},'Style 19 unknown');


    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['15_i686'],'color:purple',total[i-1]['15_x86_64'],'color:gold',total[i-1]['15_unkn'],'color:grey',total[i-1]['16_i686'],'color:teal',total[i-1]['16_x86_64'],'color:olive',total[i-1]['16_unkn'],'color:darkgrey',total[i-1]['19_i686'],'color:orange',total[i-1]['19_x86_64'],'color:tomato',total[i-1]['19_unkn'],'color:lightsalmon'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['purple','gold','grey','teal','olive','darkgrey','orange','tomato','lightsalmon'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}

function build_data_per_month_flavour_arch(data,title){
    var total=[];
    for (var i=0 ; i < 12; i++){
        total[i]={'client_i686':0,'client_x86_64':0,'client_unkn':0,'server_i686':0,'server_x86_64':0,'server_unkn':0,'desktop_i686':0,'desktop_x86_64':0,'desktop_unkn':0,'other_i686':0,'other_x86_64':0,'other_unkn':0};
        if (! data[i]){
            continue;
        }
        for (var rel in data[i]){
            for (var fla in data[i][rel]){
                for (var arch in data[i][rel][fla]){
                    total[i][fla+'_'+arch]+=data[i][rel][fla][arch];
                }
            }
        }

    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total client x86');
    data_table.addColumn({type:'string',role:'style'},'Style client x86');
    data_table.addColumn('number','Total client x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style client x86_64');
    data_table.addColumn('number','Total client unknown');
    data_table.addColumn({type:'string',role:'style'},'Style client unknown');
    data_table.addColumn('number','Total server x86');
    data_table.addColumn({type:'string',role:'style'},'Style server x86');
    data_table.addColumn('number','Total server x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style server x86_64');
    data_table.addColumn('number','Total server unknown');
    data_table.addColumn({type:'string',role:'style'},'Style server unknown');
    data_table.addColumn('number','Total desktop x86');
    data_table.addColumn({type:'string',role:'style'},'Style desktop x86');
    data_table.addColumn('number','Total desktop x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style desktop x86_64');
    data_table.addColumn('number','Total desktop unknown');
    data_table.addColumn({type:'string',role:'style'},'Style desktop unknown');
    data_table.addColumn('number','Total other x86');
    data_table.addColumn({type:'string',role:'style'},'Style other x86');
    data_table.addColumn('number','Total other x86_64');
    data_table.addColumn({type:'string',role:'style'},'Style other x86_64');
    data_table.addColumn('number','Total other unknown');
    data_table.addColumn({type:'string',role:'style'},'Style other unknown');


    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['client_i686'],'color:goldenrod',total[i-1]['client_x86_64'],'color:gold',total[i-1]['client_unkn'],'color:lightgrey',total[i-1]['server_i686'],'color:darkviolet',total[i-1]['server_x86_64'],'color:deeppink',total[i-1]['server_unkn'],'color:grey',total[i-1]['desktop_i686'],'color:slateblue',total[i-1]['desktop_x86_64'],'color:skyblue',total[i-1]['desktop_unkn'],'color:darkgrey',total[i-1]['other_i686'],'color:plum',total[i-1]['other_x86_64'],'color:pink',total[i-1]['other_unkn'],'color:black'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['goldenrod','gold','lightgrey','darkviolet','deeppink','grey','slateblue','skyblue','darkgrey','plum','pink','black'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 9 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_releases_mem(data,title){
    var total=[];
    var sizes=['unkn','2G','4G','8G']
    for (var i=0 ; i < 12; i++){
        total[i]={'15_2G':0,'15_4G':0,'15_8G':0,'15_unkn':0,'16_2G':0,'16_4G':0,'16_8G':0,'16_unkn':0,'19_2G':0,'19_4G':0,'19_8G':0,'19_unkn':0};
        for (var size in sizes){
            if (! data[sizes[size]][i]){
                continue;
            }
            for (var rel in data[sizes[size]][i]){
                for (var fla in data[sizes[size]][i][rel]){
                    total[i][rel+'_'+sizes[size]]+=data[sizes[size]][i][rel][fla];
                }
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total 15 < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style 15 < 2G');
    data_table.addColumn('number','Total 15 < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style 15 < 4G');
    data_table.addColumn('number','Total 15 > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style 15 > 4G');
    data_table.addColumn('number','Total 15 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 15 unknown');
    data_table.addColumn('number','Total 16 < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style 16 < 2G');
    data_table.addColumn('number','Total 16 < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style 16 < 4G');
    data_table.addColumn('number','Total 16 > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style 16 > 4G');
    data_table.addColumn('number','Total 16 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 16 unknown');
    data_table.addColumn('number','Total 19 < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style 19 < 2G');
    data_table.addColumn('number','Total 19 < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style 19 < 4G');
    data_table.addColumn('number','Total 19 > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style 19 > 4G');
    data_table.addColumn('number','Total 19 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 19 unknown');
    

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['15_2G'],'color:darkgoldenrod',total[i-1]['15_4G'],'color:goldenrod',total[i-1]['15_8G'],'color:gold',total[i-1]['15_unkn'],'color:lightgrey',total[i-1]['16_2G'],'color:darkviolet',total[i-1]['16_4G'],'color:deeppink',total[i-1]['16_8G'],'color:pink',total[i-1]['16_unkn'],'color:darkgrey',total[i-1]['19_2G'],'color:palegreen',total[i-1]['19_4G'],'color:springgreen',total[i-1]['19_8G'],'color:green',total[i-1]['19_unkn'],'color:darkseagreen',])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['darkgoldenrod','goldenrod','gold','lightgrey','darkviolet','deeppink','pink','darkgrey','palegreen','springgreen','green','darkseagreen'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_mem(data,title){
    var total=[];
    var sizes=['unkn','2G','4G','8G']
    for (var i=0 ; i < 12; i++){
        total[i]={'unkn':0,'2G':0,'4G':0,'8G':0};
        for (var size in sizes){
            if (! data[sizes[size]][i]){
                continue;
            }
            for (var rel in data[sizes[size]][i]){
                for (var fla in data[sizes[size]][i][rel]){
                    total[i][sizes[size]]+=data[sizes[size]][i][rel][fla];
                }
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style < 2G');
    data_table.addColumn('number','Total < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style < 4G');
    data_table.addColumn('number','Total > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style > 4G');
    data_table.addColumn('number','Total unknown');
    data_table.addColumn({type:'string',role:'style'},'Style unknown');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['2G'],'color:gold',total[i-1]['4G'],'color:red',total[i-1]['8G'],'color:blue',total[i-1]['unkn'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['gold','red','blue','grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_flavours_mem(data,title){
    var total=[];
    var sizes=['unkn','2G','4G','8G']
    for (var i=0 ; i < 12; i++){
        total[i]={'client_2G':0,'client_4G':0,'client_8G':0,'client_unkn':0,'server_2G':0,'server_4G':0,'server_8G':0,'server_unkn':0,'desktop_2G':0,'desktop_4G':0,'desktop_8G':0,'desktop_unkn':0,'other_2G':0,'other_4G':0,'other_8G':0,'other_unkn':0};
        for (var size in sizes){
            if (! data[sizes[size]][i]){
                continue;
            }
            for (var rel in data[sizes[size]][i]){
                for (var fla in data[sizes[size]][i][rel]){
                    total[i][fla+'_'+sizes[size]]+=data[sizes[size]][i][rel][fla];
                }
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total client < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style client < 2G');
    data_table.addColumn('number','Total client < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style client < 4G');
    data_table.addColumn('number','Total client > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style client > 4G');
    data_table.addColumn('number','Total client > unknown');
    data_table.addColumn({type:'string',role:'style'},'Style client unknown');
    data_table.addColumn('number','Total server < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style server < 2G');
    data_table.addColumn('number','Total server < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style server < 4G');
    data_table.addColumn('number','Total server > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style server > 4G');
    data_table.addColumn('number','Total server unknown');
    data_table.addColumn({type:'string',role:'style'},'Style server unknown');
    data_table.addColumn('number','Total desktop < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style desktop < 2G');
    data_table.addColumn('number','Total desktop < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style desktop < 4G');
    data_table.addColumn('number','Total desktop > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style desktop > 4G');
    data_table.addColumn('number','Total desktop unknown');
    data_table.addColumn({type:'string',role:'style'},'Style desktop unknown');
    data_table.addColumn('number','Total other < 2G');
    data_table.addColumn({type:'string',role:'style'},'Style other < 2G');
    data_table.addColumn('number','Total other < 4G');
    data_table.addColumn({type:'string',role:'style'},'Style other < 4G');
    data_table.addColumn('number','Total other > 4G');
    data_table.addColumn({type:'string',role:'style'},'Style other > 4G');
    data_table.addColumn('number','Total other unknown');
    data_table.addColumn({type:'string',role:'style'},'Style other unknown');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['client_2G'],'color:darkgoldenrod',total[i-1]['client_4G'],'color:goldenrod',total[i-1]['client_8G'],'color:gold',total[i-1]['client_unkn'],'color:lightgrey',total[i-1]['server_2G'],'color:darkviolet',total[i-1]['server_4G'],'color:deeppink',total[i-1]['server_8G'],'color:pink',total[i-1]['server_unkn'],'color:grey',total[i-1]['desktop_2G'],'color:slateblue',total[i-1]['desktop_4G'],'color:skyblue',total[i-1]['desktop_8G'],'color:blue',total[i-1]['desktop_unkn'],'color:darkgrey',total[i-1]['other_2G'],'color:teal',total[i-1]['other_4G'],'color:darkkhaki',total[i-1]['other_8G'],'color:green',total[i-1]['other_unkn'],'color:black'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['darkgoldenrod','goldenrod','gold','lightgrey','darkviolet','deeppink','pink','grey','slateblue','skyblue','blue','darkgrey','teal','darkkhaki','green','black'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 9 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}

function build_data_per_month_ltsp_usage(data,title){
    var total=[];
    var group_items=3
    for (var i=0 ; i < 12*group_items; i++){
        var item_no=Math.floor(i/group_items)
        if (! data[i]){
            continue;
        }
        if (! total[item_no]){
            total[item_no]={0:0,1:0,'unkn':0}
        }
        total[item_no][data[i][0]]=parseInt(data[i][1])
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total normal clients');
    data_table.addColumn({type:'string',role:'style'},'Total normal clients style');
    data_table.addColumn('number','Total ltsp clients');
    data_table.addColumn({type:'string',role:'style'},'Total ltsp clients style');
    data_table.addColumn('number','Total unknown clients');
    data_table.addColumn({type:'string',role:'style'},'Total unknown clients style');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1][0],'color:purple',total[i-1][1],'color:gold',total[i-1]['unkn'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['purple','gold','grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}

}
function build_data_per_month_ltsp_modes(data,title){
    var total=[];
    var group_items=4
    for (var i=0 ; i < 12*group_items; i++){
        var item_no=Math.floor(i/group_items)
        if (! data[i]){
            continue;
        }
        if (! total[item_no]){
            total[item_no]={'thin':0,'semi':0, 'fat':0, 'unkn':0}
        }
        total[item_no][data[i][0]]=parseInt(data[i][1])
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total thin clients');
    data_table.addColumn({type:'string',role:'style'},'Total thin clients style');
    data_table.addColumn('number','Total semi clients');
    data_table.addColumn({type:'string',role:'style'},'Total semi clients style');
    data_table.addColumn('number','Total fat clients');
    data_table.addColumn({type:'string',role:'style'},'Total fat clients style');
    data_table.addColumn('number','Total unknown clients');
    data_table.addColumn({type:'string',role:'style'},'Total unknown clients style');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['thin'],'color:purple',total[i-1]['semi'],'color:gold',total[i-1]['fat'],'color:olive',total[i-1]['unkn'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format: '#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['purple','gold','olive', 'grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}

}
function build_data_per_month_releases_cpu(data,title){
    var total=[];
    var sizes=['unkn','mono','dualquad','more']
    for (var i=0 ; i < 12; i++){
        total[i]={'15_mono':0,'15_dualquad':0,'15_more':0,'15_unkn':0,'16_mono':0,'16_dualquad':0,'16_more':0,'16_unkn':0,'19_mono':0,'19_dualquad':0,'19_more':0,'19_unkn':0};
        for (var size in sizes){
            if (! data[sizes[size]][i]){
                continue;
            }
            for (var rel in data[sizes[size]][i]){
                for (var fla in data[sizes[size]][i][rel]){
                    total[i][rel+'_'+sizes[size]]+=data[sizes[size]][i][rel][fla];
                }
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total 15 mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style 15 mono processor');
    data_table.addColumn('number','Total 15 dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style 15 dual or quad processor');
    data_table.addColumn('number','Total 15 more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style 15 more than quad processor');
    data_table.addColumn('number','Total 15 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 15 unknown');
    data_table.addColumn('number','Total 16 mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style 16 mono processor');
    data_table.addColumn('number','Total 16 dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style 16 dual or quad processor');
    data_table.addColumn('number','Total 16 more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style 16 more than quad processor');
    data_table.addColumn('number','Total 16 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 16 unknown');
    data_table.addColumn('number','Total 19 mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style 19 mono processor');
    data_table.addColumn('number','Total 19 dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style 19 dual or quad processor');
    data_table.addColumn('number','Total 19 more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style 19 more than quad processor');
    data_table.addColumn('number','Total 19 unknown');
    data_table.addColumn({type:'string',role:'style'},'Style 19 unknown');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['15_mono'],'color:darkgoldenrod',total[i-1]['15_dualquad'],'color:goldenrod',total[i-1]['15_more'],'color:gold',total[i-1]['15_unkn'],'color:lightgrey',total[i-1]['16_mono'],'color:darkviolet',total[i-1]['16_dualquad'],'color:deeppink',total[i-1]['16_more'],'color:pink',total[i-1]['16_unkn'],'color:darkgrey',total[i-1]['19_mono'],'color:palegreen',total[i-1]['19_dualquad'],'color:springgreen',total[i-1]['16_more'],'color:green',total[i-1]['16_unkn'],'color:darkseagreen'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['darkgoldenrod','goldenrod','gold','lightgrey','darkviolet','deeppink','pink','darkgrey','palegreen','springgreen','green','darkseagreen'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_cpu(data,title){
    var total=[];
    var sizes=['unkn','mono','dualquad','more']
    for (var i=0 ; i < 12; i++){
        total[i]={'unkn':0,'mono':0,'dualquad':0,'more':0};
        for (var size in sizes){
            if (! data[sizes[size]][i]){
                continue;
            }
            for (var rel in data[sizes[size]][i]){
                for (var fla in data[sizes[size]][i][rel]){
                    total[i][sizes[size]]+=data[sizes[size]][i][rel][fla];
                }
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style mono processor');
    data_table.addColumn('number','Total dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style dual or quad processor');
    data_table.addColumn('number','Total more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style more than quad processor');
    data_table.addColumn('number','Total unknown');
    data_table.addColumn({type:'string',role:'style'},'Style unknown');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['mono'],'color:gold',total[i-1]['dualquad'],'color:red',total[i-1]['more'],'color:blue',total[i-1]['unkn'],'color:grey'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['gold','red','blue','grey'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 10 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_per_month_flavours_cpu(data,title){
    var total=[];
    var sizes=['unkn','mono','dualquad','more']
    for (var i=0 ; i < 12; i++){
        total[i]={'client_mono':0,'client_dualquad':0,'client_more':0,'client_unkn':0,'server_mono':0,'server_dualquad':0,'server_more':0,'server_unkn':0,'desktop_mono':0,'desktop_dualquad':0,'desktop_more':0,'desktop_unkn':0,'other_mono':0,'other_dualquad':0,'other_more':0,'other_unkn':0};
        for (var size in sizes){
            if (! data[sizes[size]][i]){
                continue;
            }
            for (var rel in data[sizes[size]][i]){
                for (var fla in data[sizes[size]][i][rel]){
                    total[i][fla+'_'+sizes[size]]+=data[sizes[size]][i][rel][fla];
                }
            }
        }
    }
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Date');
    data_table.addColumn('number','Total client mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style client mono processor');
    data_table.addColumn('number','Total client dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style client dual or quad processor');
    data_table.addColumn('number','Total client more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style client more than quad processor');
    data_table.addColumn('number','Total client unknown processor');
    data_table.addColumn({type:'string',role:'style'},'Style client unknown processor');
    data_table.addColumn('number','Total server mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style server mono processor');
    data_table.addColumn('number','Total server dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style server dual or quad processor');
    data_table.addColumn('number','Total server more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style server more than quad processor');
    data_table.addColumn('number','Total server unknown processor');
    data_table.addColumn({type:'string',role:'style'},'Style server unknown processor');
    data_table.addColumn('number','Total desktop mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style desktop mono processor');
    data_table.addColumn('number','Total desktop dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style desktop dual or quad processor');
    data_table.addColumn('number','Total desktop more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style desktop more than quad processor');
    data_table.addColumn('number','Total desktop unknown processor');
    data_table.addColumn({type:'string',role:'style'},'Style desktop unknown processor');
    data_table.addColumn('number','Total other mono processor');
    data_table.addColumn({type:'string',role:'style'},'Style other mono processor');
    data_table.addColumn('number','Total other dual or quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style other dual or quad processor');
    data_table.addColumn('number','Total other more than quad processor');
    data_table.addColumn({type:'string',role:'style'},'Style other more than quad processor');
    data_table.addColumn('number','Total other unknown processor');
    data_table.addColumn({type:'string',role:'style'},'Style other unknown processor');

    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,total[i-1]['client_mono'],'color:darkgoldenrod',total[i-1]['client_dualquad'],'color:goldenrod',total[i-1]['client_more'],'color:gold',total[i-1]['client_unkn'],'color:lightgrey',total[i-1]['server_mono'],'color:darkviolet',total[i-1]['server_dualquad'],'color:deeppink',total[i-1]['server_more'],'color:pink',total[i-1]['server_unkn'],'color:grey',total[i-1]['desktop_mono'],'color:slateblue',total[i-1]['desktop_dualquad'],'color:skyblue',total[i-1]['desktop_more'],'color:blue',total[i-1]['desktop_unkn'],'color:darkgrey',total[i-1]['other_mono'],'color:teal',total[i-1]['other_dualquad'],'color:darkkhaki',total[i-1]['other_more'],'color:green',total[i-1]['other_unkn'],'color:black'])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
                    curveType: 'function', 
                    isStacked: false,
                    hAxis:{title:'Months',ticks:dates_axis,format:'MMM'},
                    vAxis:{title:'Num instances',viewWindow : {min:0},format:'#'},
                    legend:{textStyle:{fontSize: 10}},
                    chartArea:{left:'5%',right:'10%'},
                    focusTarget: 'category',
                    colors: ['darkgoldenrod','goldenrod','gold','lightgrey','darkviolet','deeppink','pink','grey','slateblue','skyblue','blue','darkgrey','teal','darkkhaki','green','black'],
                    lineWidth: 5,
		    tooltip: { textStyle: { fontSize: 9 } },
		    backgroundColor: 'transparent',
                    };
    return {data:data_table,options:options}
}
function build_data_from_array(data,title){
    var dates_axis=[];
    var d= new Date();
    var data_table = new google.visualization.DataTable();
    data_table.addColumn({type:'date',role:'domain'},'Nhosts');
    data_table.addColumn('number',title);
    date_values=[];
    for (i=1;i <= 12;i++){
        month=d.getMonth();
        year=d.getFullYear();
        date_to_add=new Date(year,month)
        dates_axis.push(date_to_add);
        date_values.push([date_to_add,data[i-1]])
        d.setMonth(month-1);
    }
    data_table.addRows(date_values);
    var options= {  title: title, 
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
	    json = JSON.parse(json);
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
		                chart_data[type]['releases']['graph']=build_data_per_month_releases(json[key][type],'Number instances by release per month')
		                chart_data[type]['releases']['title']='Number instances by release per month';
		                chart_data[type]['flavours']['graph']=build_data_per_month_flavours(json[key][type],'Number instances by flavour per month')
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
		                chart_data[type]['global']['graph']=build_data_per_month_arch(json[key][type],'Architectures per month');
		                chart_data[type]['global']['title']='Architectures distribution per month'
		                chart_data[type]['releases']['graph']=build_data_per_month_release_arch(json[key][type],'Architectures by release per month');
		                chart_data[type]['releases']['title']='Architectures distribution by release per month'
		                chart_data[type]['flavours']['graph']=build_data_per_month_flavour_arch(json[key][type],'Architectures by flavour per month');
		                chart_data[type]['flavours']['title']='Architectures distribution by flavour per month'
		                break;
		            case 'mem':
		                if (! chart_data[type]){
		                    chart_data[type]={'global':{},'releases':{},'flavours':{}};
		                    chart_data[type]['title']='Memory';
		                }
		                chart_data[type]['global']['graph']=build_data_per_month_mem(json[key][type],'Memory per month');
		                chart_data[type]['global']['title']='Memory distribution per month'
		                chart_data[type]['releases']['graph']=build_data_per_month_releases_mem(json[key][type],'Memory by release per month');
		                chart_data[type]['releases']['title']='Memory distribution by release per month'
		                chart_data[type]['flavours']['graph']=build_data_per_month_flavours_mem(json[key][type],'Memory by flavour per month');
		                chart_data[type]['flavours']['title']='Memory distribution by flavour per month'
		                break;
		            case 'cpu':
		                if (! chart_data['cpu']){
		                    chart_data['cpu']={'global':{},'releases':{},'flavours':{}};
		                    chart_data['cpu']['title']='CpuS';
		                }
		                chart_data['cpu']['global']['graph']=build_data_per_month_cpu(json[key][type],'Number CpuS per month');
		                chart_data['cpu']['global']['title']='Number CpuS distribution per month'
		                chart_data['cpu']['releases']['graph']=build_data_per_month_releases_cpu(json[key][type],'Number CpuS by release per month');
		                chart_data['cpu']['releases']['title']='Number CpuS distribution by release per month'
		                chart_data['cpu']['flavours']['graph']=build_data_per_month_flavours_cpu(json[key][type],'Number CpuS by release per month');
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
		                        chart_data['ltsp']['usage']['graph']=build_data_per_month_ltsp_usage(json[key][type],'LTSP usage per month')
		                        chart_data['ltsp']['usage']['title']='LTSP Use'
		                    }
		                }
		                if (type == 'count_mode'){
		                    if (! chart_data['ltsp']['modes']){
		                        chart_data['ltsp']['modes']={}
		                        chart_data['ltsp']['modes']['graph']=build_data_per_month_ltsp_modes(json[key][type],'LTSP type by type per month')
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
				        chart_data[tapp]['releases']['graph']=build_data_per_month_releases(json[key][app_num]['app_use'],'Application use by release per month ('+app+')');
				        chart_data[tapp]['releases']['title']='Use per month for application '+app;
				        chart_data[tapp]['flavours']={};
				        chart_data[tapp]['flavours']['graph']=build_data_per_month_flavours(json[key][app_num]['app_use'],'Application use by flavour per month ('+app+')');
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
                if (tables_per_flavour == 1){
                    titles=['Top apps from '+init_range+' until '+end_range]
                }else{
                    titles=['Top apps este mes','Top apps ultimo mes','Top apps penultimo mes'];
                }
                divname='chart_'+distro+'_'+sabor;
                $('#accordion').append('<h3>Distro '+distro+'('+sabor+')</h3>');
                $('#accordion').append('<div class="'+divname+'"></h3>');
                for (i=0; i<tables_per_flavour; i++){
                    $('div.'+divname).append('<div id="'+divname+i+'"></div>');
                    k=0;
                    var datos=new google.visualization.DataTable();
                    datos.addColumn('string','App');
                    datos.addColumn('number','Count');
                    $.each(json[distro][sabor][i][0],function(key,value){
                        //console.log( i+':'+k+'->'+key + " : " + value );
                        datos.addRow([key,parseInt(value)]);
                        k++;
                    })
                    while (k < 10){
                        datos.addRow(['',0]);
                        k++;
                    }
                    obj.push(datos);
                    //console.log('drawing:'+titles[i]+' into '+divname+i);
                    titles[i]=titles[i]+' (Total clients: '+json[distro][sabor][i][1]['nclients']+')'
                    drawChart(obj[obj.length-1],titles[i],divname+i,k);
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
    $('#stats_box').append('<span class="stats">Load time: '+((end_load_time-start_load_time)/1000).toString()+' sec</span>')
    $('#stats_box').append('<span class="stats">Get time: '+parseFloat(((end_get_time-start_get_time)/1000)-q_time).toFixed(3).toString()+' sec</span>')
    $('#stats_box').append('<span class="stats">Graph time: '+((gr_time-start_graph_time)/1000).toString()+' sec</span>')
    $('#stats_box').append('<span class="stats">Query time: '+parseFloat(q_time).toFixed(3).toString()+' sec</span>')
    $('#stats_box').append('<span class="stats">Updated: '+keep_alive.toString()+'</span>')
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
