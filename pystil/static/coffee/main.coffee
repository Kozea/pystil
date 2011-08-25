$ () =>
    elts = []
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

    for elt in $(".graph")
        elt = $ elt
        elts.push(new @[elt.attr('data-graph')](elt))



