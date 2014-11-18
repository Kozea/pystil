commands = (
    INFO: (m) ->
        console.log(m)
    VISIT: (m) ->
        if $('table.last').size()
            pipe = m.indexOf('|')
            site = m.substr(0, pipe)
            line = m.substr(pipe + 1)
            $line = $ line

            site_filter = $('table.last').attr('data-site')
            if site_filter == 'all' or site.indexOf(site_filter) > -1
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
    EXIT: (uuid) ->
        $("table.last tr[data-visit-uuid=#{uuid}]").removeClass 'active'
)

$ ->
    host = location.host
    if host.indexOf(':')
        host = host.split(':')[0]
    window.last_visit_ws = last_visit_ws = new WebSocket("#{if location.protocol == 'https:' then 'wss' else 'ws'}://#{host}:#{window._pystil_port}/last_visits")

    last_visit_ws.onopen = ->
        console.log('Last visits websocket opened', arguments)

    last_visit_ws.onerror = ->
        console.log('Last visits websocket errored', arguments)

    last_visit_ws.onmessage = (evt) ->
        message = evt.data
        pipe = message.indexOf('|')
        if pipe > -1
            cmd = message.substr(0, pipe)
            data = message.substr(pipe + 1)
            commands[cmd] data
