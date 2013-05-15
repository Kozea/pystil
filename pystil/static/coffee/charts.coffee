$ ->
    $('.datepicker').datepicker(
        dateFormat: 'yy-mm-dd'
        maxDate: new Date()
    )
    get_dates = ->
        $.datepicker.formatDate('yy-mm-dd', $("#from").datepicker("getDate")) + '/' +
                $.datepicker.formatDate('yy-mm-dd', $("#to").datepicker("getDate"))

    make_url = (url) ->
        if url.indexOf('/load') != 0
            url = '/load' + url

        if url.indexOf('/between') > -1
            url = url.split('/between')[0]
        url.replace('.svg', '') + '/between/' +
             get_dates() +
            '.svg'


    $('form.from-to').on('submit', ->
        $('embed').each(->
            url = make_url($(@).attr('src'))
            after_load = ($old, $new) ->
                setTimeout (->
                    $new.trigger('load')
                    setTimeout (->
                        load_embed_maybe $new
                    ), 100
                ), 100

            load_embed_maybe @, url, after_load
        )
        false
    )

    if $('.datepicker').length
        $("#from").datepicker("setDate", '-1m')
        $("#to").datepicker("setDate", new Date())

    load_embed_maybe = (embed, url=null, callback=null) ->
        if $(embed).closest('figure').data('loading')
            setTimeout (-> load_embed_maybe(embed, url, callback)), 250
            return
        $new = load_embed embed, url
        if callback
            callback $(embed), $new

    load_embed = (embed, url=null) ->
        $loading = $ embed
        url = url or make_url($loading.attr('src')).replace('/load', '')
        $figure = $loading.closest('figure')
        $figure.data('loading', true)
        if not $figure.attr('style')
            $figure.width($loading.width()).height($loading.height()).css(overflow: 'hidden')
        $figure.append(
            $new = $('<embed>', type: 'image/svg+xml', src: url)
            .on('load', ->
                $(this).prev().remove()
                $(this).closest('figure').data('loading', false)
            ))
        $new

    $('embed[src^="/load"]').on('load', -> load_embed(@))

    $(window).bind('popstate', (event) ->
        if event.originalEvent.state and event.originalEvent.state.page
            fetch event.originalEvent.state.page, document.location.href, true
    )

    fetch = (page, url, popping) ->
        $('#container').load(url, xhr: true, ->
            $('embed[src^="/load"]').on('load', -> load_embed(@))
            $('nav.xhr a').removeClass('active')
            $('nav.xhr a[data-page=' + page + ']').addClass('active')
            if not popping
                history and history.pushState and history.pushState page: page, null, url
        )
    $('nav.xhr a').click(->
        page = $(@).attr('data-page')
        url = $(@).attr('href')
        fetch page, url
        false
    )
    if $('nav.xhr a.active').size()
        history and history.pushState and history.pushState page: $('nav.xhr a.active').attr('data-page'), null, document.location.href
