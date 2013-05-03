i18n = fr:
    ' on ': ' le '
    'visits': 'visites'
    ' visits at ': 'visites à '

class @Base
    constructor: (@elt) ->
        @elt.addClass 'loading'
        @criteria = @elt.attr("data-criteria").split ','
        @lang = @elt.attr('data-lang') or 'us'
        @remaining_criteria = @criteria.length
        setTimeout @fetch, 50

    _: (text) =>
        return if i18n[@lang] then i18n[@lang][text] else text

    fetch: =>
        $.ajax
            url: (window.pystil_site or '') + '/data'
            type: 'POST'
            data: @post_data()
            dataType: if window.pystil_site then 'jsonp' else 'json'
            success: @reply

    clear: =>
        @remaining_criteria = @criteria.length

    reply: (response) =>
        @elt.removeClass 'loading'
        if @remaining_criteria > 0
            @fetch()

    post_data: =>
        site: if not window.pystil_site then location.pathname.split("/")[2] or "all" else @elt.attr("data-site") or window.pystil_data_site or location.hostname
        graph: @type
        criteria: @criteria[--@remaining_criteria]
        lang: @lang
        stamp: if @stamp and @stamp != -1 then @stamp else undefined
        from: if window.fromDate and @stamp != -1 then window.fromDate.getTime() - window.fromDate.getTimezoneOffset() * 60000 else undefined
        to: if window.toDate and @stamp != -1 then window.toDate.getTime() - window.toDate.getTimezoneOffset() * 60000 else undefined
        uuid: window.pystil_key
