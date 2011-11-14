$ () =>
    elts = []
    xhr = null
    requestIndex = 0
    $('.datepicker').datepicker(
        onSelect: (d, inst) =>
            @[inst.id + "Date"] = $.datepicker.parseDate('yy-mm-dd', d)
            for elt in elts
                if elt.plotable
                    elt.clear()
                    elt.fetch()
        dateFormat: 'yy-mm-dd'
        maxDate: new Date()
    )
    if $('.datepicker').length
        $("#from").datepicker("setDate", '-1m')
        $("#to").datepicker("setDate", new Date())
        @fromDate = $("#from").datepicker("getDate")
        @toDate = $("#to").datepicker("getDate")

    $('#filter').keyup (e) ->
        $this = $ this
        $results = $ 'section.results'
        if !$this.val()
            return
        $results.addClass 'loading'
        if xhr
            xhr.abort
        xhr = $.ajax
            url: "/sites/#{$this.val()}"
            dataType: "text"
            rqIndex: ++requestIndex
            success: (data) ->
                $results.removeClass 'loading'
                if @rqIndex is requestIndex
                    $results.html data
            error: () ->
                if @rqIndex is requestIndex
                    $results.html ""

    load_graph = (elt) ->
        if not elt.data 'loaded'
            elts.push(new @[elt.attr('data-graph')](elt))
            elt.data 'loaded', true


    $('.tab').tabshow () ->
        $('.graph', @).each (i, e) ->
            load_graph($ e)

    if not @tabs().length
        for elt in $(".graph").filter(":visible")
            load_graph $ elt
