class Map extends Base
    constructor: (@elt) ->
        super
        @make_tooltip
    reply: (response) =>
        super
        for country in response.list
            $("#" + country.key.split("$")[1].toLowerCase())
                .css(fill: 'rgba(0, 0, 255, ' + ((country.count / response.max) * 0.7 + 0.2) + ')')
                .prepend($('<title>').text(country.key.split("$")[0].toLowerCase() + ": " + country.count))

    url: () => location.href + "_by_visit.json"
    make_tooltip: () ->
        $("body").append($('<div>').attr('id', 'tooltip').css(position: 'absolute', display: 'none'))
        $(".country").mouseover (e) ->
            $('#tooltip').css(top: e.pageY + 10 + 'px', left: e.pageX + 10 + 'px', display: 'block'
            ).text($('title', e.currentTarget).text())
        $(".country").mouseout (e) -> $('#tooltip').css(display: 'none')
