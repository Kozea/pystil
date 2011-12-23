class @Last extends @Base
    type: 'last'

    constructor: (@elt) ->
        @stamp = -1
        super
        @elt.append(table = $('<table>')
                .append($('<thead>')
                    .append(tr = $('<tr>'))))
        @keys = if @elt.attr('data-columns') then @elt.attr('data-columns').split(/, ?/) else ['date', 'site' , 'ip', 'country', 'city', 'page', 'referrer']
        for col in @keys
            tr.append($('<th>').text(col.capitalize()))
        table.append(@tbody = $('<tbody>'))

    reply: (response) =>
        super
        @update(response)

    ask_update: () =>
        @remaining_criteria = 1  # Fix this
        $.ajax
            url: @url()
            method: 'GET'
            data: if window.pystil_key then uuid: window.pystil_key else undefined
            dataType: if window.pystil_site then 'jsonp' else 'json'
            success: @update

    update: (response) =>
        for visit in response.list
            now = new Date()
            visit.date = new Date(visit.date)
            if visit.date.toLocaleDateString() == now.toLocaleDateString()
                visit.date = visit.date.toLocaleTimeString()
            else
                visit.date = visit.date.toLocaleDateString() + ' - ' + visit.date.toLocaleTimeString()
            visit.date = visit.date.toString()
            @tbody.prepend(tr = $('<tr>').addClass("new-visit"))
            for col in @keys
                tr.append($('<td>').text(visit[col]))

            if @tbody.children().length > 10
                @tbody.children().last().remove()

        setTimeout(
            () ->
                $(".new-visit").each(
                    (i, elt) -> $(elt).removeClass("new-visit")
                )
        , 3000)
        @stamp = response.stamp
        setTimeout(@ask_update, 1)
