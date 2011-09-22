class @Last extends @Base
    type: 'last'

    constructor: (@elt) ->
        @stamp = 0
        super
        @elt.append(table = $('<table>')
                .append($('<thead>')
                    .append(tr = $('<tr>'))))
        for col in ["Date", "Site", "Ip", "Country", "City", "Page", "Referrer"]
            tr.append($('<th>').text(col))
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
        if response.list.length > 0
            for i in [1..response.list.length]
                @tbody.children().last().remove()

        for visit in response.list
            @tbody
                .prepend($('<tr>').addClass("new-visit")
                .append($('<td>').text(visit.date))
                .append($('<td>').text(visit.host))
                .append($('<td>').text(visit.ip))
                .append($('<td>').text(visit.country))
                .append($('<td>').text(visit.city))
                .append($('<td>').text(visit.page))
                .append($('<td>').text(visit.referrer)))

        setTimeout(
            () ->
                $(".new-visit").each(
                    (i, elt) -> $(elt).removeClass("new-visit")
                )
        , 1000)
        @stamp = response.stamp
        setTimeout(@ask_update, 1000)

