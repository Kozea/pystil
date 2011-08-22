draw = () =>
    $(".graph").each((i, elt) ->
        elt = $ elt
        if elt.hasClass("pie")
            new Pie(elt)
        else if elt.hasClass("line")
            new Line(elt)
        else if elt.hasClass("bar")
            if elt.hasClass("time")
                new TimeBar(elt)
            else
                new Bar(elt)
    )

$(draw)
