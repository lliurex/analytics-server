function send_query_month(){
    let init_selected=$("#init_date_search>option:selected").val();
    let window_selected=$("#date_window_search>option:selected").val();
    window.location.href=window.location.pathname+"?init="+init_selected+"&window="+window_selected;
}
function reload_without_params(){
    window.location.href=window.location.pathname;
}
function make_month_window(){
    $("#date_window_search").empty()
    let ysel=Number($("#init_date_search>option:selected").val().substr(0,4))
    let msel=Number($("#init_date_search>option:selected").val().substr(4))
    let date=new Date()
    let y = date.getFullYear()
    let m = date.getMonth()+2
    let num = 0
    if (ysel == y){
        num = Math.abs(m - msel)
    }else{
        num = 12 - msel + m
    }
    for (let i=1;i<=num;i++){
        $("#date_window_search").append("<option value=\""+i+"\" name=\""+i+"\">"+i+"</option>");
    }
    $("#query_box>button").unbind("click");
    $("#query_box>button").text("Show");
    $("#query_box>button")[0].disabled = false;
    $("#query_box>button").on("click",send_query_month);
}
function make_query_box(){
    let monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic" ];
    let date = new Date();
    let m = date.getMonth();
    let y = date.getFullYear();
    $("#query_box").append("<span>Custom date:");
    $("#query_box").append("Init date<span><select id=\"init_date_search\" name=\"init_date\"><option value=\"\" name=\"\"></option></select></span>");
    $("#query_box").append("Month window<span><select id=\"date_window_search\" name=\"date_window\"></select></span>");
    for (let i=0; i<12; i++){
        let date2 = new Date(y,m,1)
        let strval=date2.getFullYear().toString()+(date2.getMonth()+1).toString();
        let showval=monthNames[m]+"/"+date2.getFullYear().toString()
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
