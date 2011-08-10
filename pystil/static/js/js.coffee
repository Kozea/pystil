draw = () ->
    for g in window.graphs
        elt = $('<div>').attr('id', g.name).addClass("graph " + g.classname)
        $("#graphs").append elt
        # Keep the closures FFS
        success = ((g, elt) ->
            (response) ->
                $.plot(elt, g.data(response), g.options)
        )(g, elt)
        $.ajax
            url: g.url
            method: 'GET'
            dataType: 'json'
            success: success

        previousPoint = null
        elt.bind("plothover", ((g) -> (event, pos, item) ->
            if item
                index = if item.series.pie.show then item.seriesIndex else item.dataIndex
                if previousPoint != index
                    previousPoint = index
                    $("#tooltip").remove()
                    $('<div>').attr('id', 'tooltip').css(
                        top: pos.pageY + 5,
                        left: pos.pageX + 5,
                        border: '1px solid ' + item.series.color
                    ).text(g.tooltip item).appendTo("body")
            else
                $("#tooltip").remove()
                previousPoint = null
        )(g))

setTimeout draw, 1
