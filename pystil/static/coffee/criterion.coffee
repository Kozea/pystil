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

