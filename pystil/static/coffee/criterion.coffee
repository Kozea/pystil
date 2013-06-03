add_info = (m, cls) ->
    $('table.last').parent().find('p.query_info').remove()
    $('table.last').after($('<p>', class: 'query_info ' + cls).text(m))
    if cls == 'searching'
        dot = ->
            $s = $('p.searching')
            if $s.size()
                $s.text(($s.text() + '.').replace('....', ''))
                setTimeout(dot, 500)
        dot()

commands = (
    INFO: (m) ->
        console.log(m)
    VISIT: (m) ->
        $line = $ m
        $line.addClass 'recent'
        $('table.last tbody').append($line)
        setTimeout (->
            $line.removeClass 'recent'
        ), 500

        $('header h1 a').addClass 'pulse'
        setTimeout (->
            $('header h1 a').removeClass 'pulse'
        ), 75
    PAUSE: (m) ->
        add_info m, 'paused'

    BEGIN: (m) ->
        add_info m, 'begun'

    BUSY: (m) ->
        add_info m, 'busy'

    END: (m) ->
        if m.indexOf('Done') == 0
            add_info m, 'done'
        else
            add_info m, 'error'
)

$ ->
    if not $('.criterion').size() or not _query_criterion or not _query_value
        return

    criterion = _query_criterion
    value = _query_value

    host = location.host
    if host.indexOf(':')
        host = host.split(':')[0]
    window.query_ws = query_ws = new WebSocket("ws://#{host}:#{window._pystil_port}/query")

    query_ws.onopen = ->
        console.log('Websocket opened', arguments)
        query_ws.send("criterion|#{criterion}|#{value}")

    query_ws.onerror = ->
        console.log('Websocket errored', arguments)

    query_ws.onmessage = (evt) ->
        message = evt.data
        pipe = message.indexOf('|')
        if pipe > -1
            cmd = message.substr(0, pipe)
            data = message.substr(pipe + 1)
            commands[cmd] data

    add_info 'Searching...', 'searching'
    $(window).scroll () ->
        if $(window).scrollTop() + $(window).height() == $(document).height()
            if $('p.paused').size()
                add_info 'Searching...', 'searching'
                query_ws.send('more')

