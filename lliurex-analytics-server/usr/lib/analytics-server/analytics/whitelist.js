function put_elements(data){
    $('#loading').remove()
    $('#send').show()
    $('#configure_whitelist').show()
    var items = data
    if (items != undefined){
        if (! (items.hasOwnProperty('out') && items.hasOwnProperty('in') && items.hasOwnProperty('unk'))){
            return
        }
        for (var e=0;e<items['out'].length;e++){
            $('select[name="denied"]').append('<option value="'+items['out'][e]+'">'+items['out'][e]+'</option>')
        }
        for (var e=0;e<items['in'].length;e++){
            $('select[name="accepted"]').append('<option value="'+items['in'][e]+'">'+items['in'][e]+'</option>')
        }
        for (var e=0;e<items['unk'].length;e++){
            $('select[name="nonselected"]').append('<option value="'+items['unk'][e]+'">'+items['unk'][e]+'</option>')
        }
    }
    put_triggers()
}

function move_to(from,to){
    var orig = ''
    var dest = ''
    var elems = ''
    if (from == 'left'){
        elems = $('#nonwhitelist>select>option:selected')
        orig = $('#nonwhitelist>select')
    }else if (from == 'center'){
        elems = $('#unknown_state_whitelist>select>option:selected')
        orig = $('#unknown_state_whitelist>select')
    }else if (from == 'right'){
        elems = $('#inwhitelist>select>option:selected')
        orig = $('#inwhitelist>select')
    }
    if (to == 'left'){
        dest = $('#nonwhitelist>select')
    }else if (to == 'center'){
        dest = $('#unknown_state_whitelist>select')
    }else if (to == 'right'){
        dest = $('#inwhitelist>select')
    }
    if (orig == '' || dest == '' || elems == ''){
        return false
    }
    dest.append(elems)
    elems.each(function(){$('this').remove()})
    $('#configure_whitelist option:selected').removeAttr("selected")
}

function get_items(){
//    var state = { 'out' : [], 'unk' : [], 'into' : [] }
    var state = { 'out' : [], 'into' : [] }
    $('#nonwhitelist>select>option').each(function(){state['out'].push($(this).val())})
//    $('#unknown_state_whitelist>select>option').each(function(){state['unk'].push($(this).val())})
    $('#inwhitelist>select>option').each(function(){state['into'].push($(this).val())})
    return state
}

function send_items(){
    var state = get_items()
    $.post('PutWhitelist', {'status': JSON.stringify(state)}, function(data){
        data = data.toLowerCase()
        if (data == 'ok'){
            alert('Sending succeded')
        }else{
            alert('Sending succeded but result was Nok, '+data)
        }
    })
    .fail(function(data){
        console.log(data)
        alert('Error sending ajax requests')
    })
}

function get_dbitems(){
    $('#configure_whitelist').hide()
    $('#send').hide()
    $('body').append('<div id="loading"></div>')
    $.getJSON('GetWhitelistItems',function(data){
        put_elements(data)
    })
    .fail(function(data){
        alert('Can\'t fetch whitelist data')
        return undefined
    })
}

function filter(elem){
    var value=$(this).val().trim().toLowerCase()
    var dofilter = false
    var opts 
    if (value != ''){
        dofilter = true
    }
    opts=$(this).parent().next().find('option')
    for (var i=0;i<opts.length;i++){
        var show = true
        if (dofilter){
            show = opts[i].value.toLowerCase().includes(value)
        }
        if (show){
            $(opts[i]).show()
        }else{
            $(opts[i]).hide()
        }
    }
}
function put_triggers(){
    $('#btnleft_to_left').click(function(){move_to('center','left')})
    $('#btnleft_to_center').click(function(){move_to('left','center')})
    $('#btnright_to_right').click(function(){move_to('center','right')})
    $('#btnright_to_center').click(function(){move_to('right','center')})
    $('#send_btn').click(send_items)
    $('.filter>textarea').on("change keyup paste",filter)
}

function start(){
    get_dbitems()
}