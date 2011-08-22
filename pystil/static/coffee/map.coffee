class Map extends Base
    constructor: (@elt) ->
        @data_type = 'html'
        super

    reply: (response) =>
        super
        @elt.html response
        $.ajax
            url: @dataurl()
            method: 'GET'
            dataType: 'json'
            success: @datareply

    datareply: (response) =>
        for country in response.list
            $("#" + country.key.split("$")[1].toLowerCase())
                .css(fill: 'rgba(0, 0, 255, ' + ((country.count / response.max) * 0.7 + 0.2) + ')')
                .prepend($('<title>').text(country.key.split("$")[0].toLowerCase() + ": " + country.count))
        @make_tooltip()

    url: () =>
        "/static/worldmap.svg"

    dataurl: () =>
        @root + "map_by_visit.json"

    make_tooltip: () ->
        $("body").append($('<div>').attr('id', 'maptooltip').css(position: 'absolute', display: 'none'))
        $(".country").mouseover (e) ->
            $('#maptooltip').css(top: e.pageY + 10 + 'px', left: e.pageX + 10 + 'px', display: 'block'
            ).text($('title', e.currentTarget).text())
        $(".country").mouseout (e) -> $('#maptooltip').css(display: 'none')
