class @Base

    constructor: (@elt) ->
        @elt.addClass 'loading'
        @criteria = @elt.attr("data-criteria").split(',')
        @remaining_criteria = @criteria.length
        setTimeout(@fetch, 50)

    fetch: () =>
        $.ajax
            url: @url()
            method: 'GET'
            data: if window.pystil_key then uuid: window.pystil_key else undefined
            dataType: if window.pystil_site then 'jsonp' else 'json'
            success: @reply

    clear: () ->
        @remaining_criteria = @criteria.length

    reply: (response) =>
        @elt.removeClass 'loading'
        if @remaining_criteria > 0
            @fetch()

    url: () ->
        if window.pystil_site
            ref = window.pystil_site
            site = @elt.attr("data-site") or window.pystil_data_site  or location.hostname
        else
            ref = ""
            site = location.pathname.split("/")[1] or "all"
        ref += "/#{site}/#{@type}_by_#{@criteria[--@remaining_criteria]}"
        if @stamp
            ref += "_at_#{@stamp}"
        else if window.fromDate and window.toDate
            ref += "_from_#{window.fromDate.getTime() - window.fromDate.getTimezoneOffset() * 60000}_to_#{window.toDate.getTime() - window.toDate.getTimezoneOffset() * 60000}"
        "#{ref}.json"
