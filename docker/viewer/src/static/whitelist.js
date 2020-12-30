function get_time(){
    return (Date.now ? Date.now() : new Date().getTime())/1000 ;
}

function put_elements(data){
    $('#loading').remove()
    $('#send').show()
    $('#configure_whitelist').show()
    let items = data
    let elements = {
        'out' : $('select[name="denied"]'),
        'in' : $('select[name="accepted"]'),
        'unk' : $('select[name="nonselected"]')
    }
    let i = 0
    if (items != undefined){
        if (! (items.hasOwnProperty('out') && items.hasOwnProperty('in') && items.hasOwnProperty('unk'))){
            return
        }
        for (let key of ['out','in','unk']){
            if (! Array.isArray(items[key])){
                items[key] = [items[key]]
            }
            for (let e=0;e<items[key].length;e++){
                i++
                elements[key].append('<option value"'+items[key][e]+'">'+items[key][e]+'</option>')
            }
        }
    }
    put_triggers()
    console.log(i+' elements included')
}
function move_to(from,to){
    let orig = ''
    let dest = ''
    let elems = ''
    let stime = get_time()
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
    elems.each(function(){$('this').removeAttr("selected")})
    dest.append(elems)
    elems.each(function(){$('this').remove()})
    // $('#configure_whitelist option:selected').removeAttr("selected")
    console.log('Move in: '+(get_time()-stime).toFixed(3))
}

function get_items(){
//    let state = { 'out' : [], 'unk' : [], 'into' : [] }
    let state = { 'out' : [], 'into' : [] }
    $('#nonwhitelist>select>option').each(function(){state['out'].push($(this).val())})
//    $('#unknown_state_whitelist>select>option').each(function(){state['unk'].push($(this).val())})
    $('#inwhitelist>select>option').each(function(){state['into'].push($(this).val())})
    return state
}

function send_items(){
    let state = get_items()
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
    let stime = get_time() 
    $.getJSON('GetWhitelistItems',function(data){
        let etime = get_time()
        console.log('Get time: '+(etime-stime).toFixed(3))
        put_elements(data)
        console.log('Put time: '+(get_time()-etime).toFixed(3))
    })
    .fail(function(data){
        alert('Can\'t fetch whitelist data')
        return undefined
    })
}

function filter(elem){
    let value=$(this).val().trim().toLowerCase()
    let dofilter = false
    let opts 
    let stime = get_time()
    if (value != ''){
        dofilter = true
    }
    opts=$(this).parent().next().find('option')
    for (let i=0;i<opts.length;i++){
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
    console.log('Filter in: '+(get_time()-stime).toFixed(3))
}
function put_triggers(){
    var stime = get_time()
    $('#btnleft_to_left').click(function(){move_to('center','left')})
    $('#btnleft_to_center').click(function(){move_to('left','center')})
    $('#btnright_to_right').click(function(){move_to('center','right')})
    $('#btnright_to_center').click(function(){move_to('right','center')})
    $('#send_btn').click(send_items)
    $('.filter>textarea').on("change keyup paste",filter)
    console.log('Put triggers in: '+(get_time()-stime).toFixed(3))
}

function start(){
    get_dbitems()
}