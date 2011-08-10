$(function () {
    for(var i in graphs) {
        var g = graphs[i];
        $("#graphs").append(
            $('<div>').attr('id', g.name).addClass("graph " + g.classname));
        var elt = $("#" + g.name);
        var opt = g.options;
        var plot = $.plot(elt, [], g.options);
        // Keep the closures FFS
        var success = function (g, elt) {
            return function (response) {
                plot = $.plot(elt, g.data(response), g.options);
            };
        }(g, elt);
        $.ajax({
            url: g.url,
            method: 'GET',
            dataType: 'json',
            success: success
        });

        var previousPoint = null;
        elt.bind("plothover", function (g) {
            return function (event, pos, item) {
                if (item) {
                    var index = item.series.pie.show ? item.seriesIndex : item.dataIndex;
                    if (previousPoint != index) {
                        previousPoint = index;
                        $("#tooltip").remove();
                        $('<div>').attr('id', 'tooltip').css({
                            top: pos.pageY + 5,
                            left: pos.pageX + 5,
                            border: '1px solid ' + item.series.color
                        }).text(g.tooltip(item)).appendTo("body");
                    }
                }
                else {
                    $("#tooltip").remove();
                    previousPoint = null;
                }
            };
        }(g));
    }
});
