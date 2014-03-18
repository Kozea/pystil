# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

make_query = (track) ->
    ("#{k}=#{escape(v)}" for k, v of track).join '&'

send = (query, time) ->
    im = new Image()
    im.src = "%spystil-#{time}.gif?#{query}"

tracker = () =>
    now = new Date()
    time = now.getTime()
    c = l = null
    uuid = "%s"

    try
        c = @document.cookie.match('pystil=[0-9]+\\$(.+)')
        try
            l = @document.cookie.match('pystil=([0-9]+)')
        catch e
            0
        if c?.length > 1 and c[1] != 'undefined'
            uuid = c[1]
        @document.cookie = "pystil=#{time}$#{uuid}; path=/"
    catch e
        0
    # Get the cookie uuid or take a new one
    track =
        _: uuid
        # Resolution
        s: @screen.width + 'x' + @screen.height
        # Referrer
        r: @document.referrer
        # Url
        u: "#{@location.protocol}//#{@location.host}"
        # Host
        k: @location.hostname
        # Path
        p: @location.pathname
        # Hash
        h: @location.hash
        # Query
        q: @location.search
        # Operation, o = page openeng
        d: 'o'
        # Time zone offset
        z: -now.getTimezoneOffset()
        # Last visit or undefined
        l: (l or [])[1]
        # Language
        i: navigator.language or navigator.userLanguage or navigator.browserLanguage

    # Strip host for local referrers
    if track.r.indexOf(track.u) > -1
        track.r = track.r.replace(track.u, '')

    send(make_query(track), time)
    previous_unload = if @onunload then @onunload else ->

    @onunload = () ->
        retrack =
            _: uuid
            # Operation: c = page close
            d: 'c'
            # Time spent on site
            t: new Date().getTime() - time
        send(make_query(retrack), time)
        previous_unload()

@setTimeout (->
    try
        tracker()
    catch e
        try
            send 'd=e&r=' + e.toString(), new Date().getTime()
        catch inner
            0
), 10
