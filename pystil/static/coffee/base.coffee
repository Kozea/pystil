class @Base

    constructor: (@elt) ->
        @elt.addClass 'loading'
        @criteria = @elt.attr("data-criteria").split(',')
        @remaining_criteria = @criteria.length
        @fetch()

    fetch: () ->
        $.ajax
            url: @url()
            method: 'GET'
            dataType: 'json'
            success: @reply

    clear: () ->
        @remaining_criteria = @criteria.length

    reply: (response) =>
        @elt.removeClass 'loading'
        if @remaining_criteria > 0
            @fetch()

    url: () ->
        site = location.pathname.split("/")[1] or "all"
        ref = "/#{site}/#{@type}_by_#{@criteria[--@remaining_criteria]}"
        if @stamp
            ref += "_at_#{@stamp}"
        else
            ref += "_from_#{window.fromDate.getTime()}_to_#{window.toDate.getTime()}"
        "#{ref}.json"
