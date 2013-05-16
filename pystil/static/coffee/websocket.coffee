commands = (
    INFO: (m) ->
        console.log(m)
    VISIT: (m) ->
        if $('table.last').size()
            $line = $ m
            $line.addClass 'active'
            $line.addClass 'recent'
            $('table.last tbody').prepend($line)
            setTimeout (->
                $line.removeClass 'recent'
            ), 500

        $('header h1 a').addClass 'pulse'
        setTimeout (->
            $('header h1 a').removeClass 'pulse'
        ), 75
    EXIT: (id) ->
        id = parseInt(id)
        $("table.last tr[data-visit-id=#{id}]").removeClass 'active'
)

$ ->
    window.ws = ws = new WebSocket("ws://#{location.host}/ws")

    ws.onopen = ->
        console.log('Websocket opened', arguments)

    ws.onerror = ->
        console.log('Websocket errored', arguments)

    ws.onmessage = (evt) ->
        message = evt.data
        pipe = message.indexOf('|')
        if pipe > -1
            cmd = message.substr(0, pipe)
            data = message.substr(pipe + 1)
            commands[cmd] data
