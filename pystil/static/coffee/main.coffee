$ ->
    requestIndex = 0
    $('.datepicker').datepicker(
        dateFormat: 'yy-mm-dd'
        maxDate: new Date()
    )

    if $('.datepicker').length
        $("#from").datepicker("setDate", '-1m')
        $("#to").datepicker("setDate", new Date())

     $('#filter').keyup (e) ->
        $this = $ @
        $results = $ 'section.results'
        val = $this.val().trim()
        if !val
            val = '%'
        $results.addClass 'loading'
        if xhr
            xhr.abort
        xhr = $.ajax
            url: "/sites/#{val}"
            dataType: "text"
            rqIndex: ++requestIndex
            success: (data) ->
                $results.removeClass 'loading'
                if @rqIndex is requestIndex
                    $results.html data
            error: () ->
                if @rqIndex is requestIndex
                    $results.html ""

    $(window).bind('popstate', (event) ->
        if event.originalEvent.state and event.originalEvent.state.page
            fetch event.originalEvent.state.page, document.location.href, true
    )

    fetch = (page, url, popping) ->
        $('#container').load(url, xhr: true, ->
            window._pystil_init_embed()
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
