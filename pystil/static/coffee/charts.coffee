$ ->
    get_dates = ->
        $.datepicker.formatDate('yy-mm-dd', $("#from").datepicker("getDate")) + '/' +
                $.datepicker.formatDate('yy-mm-dd', $("#to").datepicker("getDate"))

    make_url = (url) ->
        if url.indexOf('/load') != 0
            url = '/load' + url

        if url.indexOf('/between') > -1
            url = url.split('/between')[0]
        if $('.datepicker').length
            url = url.replace('.svg', '') + '/between/' + get_dates() + '.svg'
        url

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
    $('.criterion form').on('submit', ->
        location.href = '/criterion/' + $(this).find('#criterion').val() + '/' + $(this).find('#value').val()
        false
    )
    $('i.load').click(-> $(this).closest('form').submit())

    load_embed_maybe = (embed, url=null, callback=null) ->
        if $(embed).closest('figure').data('loading') or (
            $(embed).width() == 300 and $(embed).height() == 150)
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

    window._pystil_init_embed = ->
        $('embed[src^="/load"]').on('load', -> load_embed_maybe(@))

    window._pystil_init_embed()
