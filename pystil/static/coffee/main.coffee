draw = () =>
    for elt in $(".graph")
        elt = $ elt
        new @[elt.attr('data-graph')](elt)

$ draw
