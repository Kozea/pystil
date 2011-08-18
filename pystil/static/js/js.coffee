draw = () =>
    for elt in $(".graph")
        $elt = $(elt)
        if $elt.hasClass("pie")
            g = new @Pie(elt.id)
        else if $elt.hasClass("line")
            g = new @Line(elt.id)
        else if $elt.hasClass("bar")
            if $elt.hasClass("time")
                g = new @TimeBar(elt.id)
            else
                g = new @Bar(elt.id)

        # Keep the closures FFS
        $elt.addClass('loading')
        success = ((g, $elt) ->
            (response) ->
                $elt.removeClass('loading')
                $.plot($elt, g.data(response), g.options)
        )(g, $elt)
        $.ajax
            url: g.url()
            method: 'GET'
            dataType: 'json'
            success: success

        previousPoint = null
        $elt.bind("plothover", ((g) -> (event, pos, item) ->
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

$(draw)
