(function() {
  var draw;
  draw = function() {
    var elt, g, plot, previousPoint, success, _i, _len, _ref, _results;
    _ref = window.graphs;
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      g = _ref[_i];
      $("#graphs").append($('<div>').attr('id', g.name).addClass("graph " + g.classname));
      elt = $("#" + g.name);
      plot = $.plot(elt, [], g.options);
      success = (function(g, elt) {
        return function(response) {
          return plot = $.plot(elt, g.data(response), g.options);
        };
      })(g, elt);
      $.ajax({
        url: g.url,
        method: 'GET',
        dataType: 'json',
        success: success
      });
      previousPoint = null;
      _results.push(elt.bind("plothover", (function(g) {
        return function(event, pos, item) {
          var index;
          if (item) {
            index = item.series.pie.show ? item.seriesIndex : item.dataIndex;
            if (previousPoint !== index) {
              previousPoint = index;
              $("#tooltip").remove();
              return $('<div>').attr('id', 'tooltip').css({
                top: pos.pageY + 5,
                left: pos.pageX + 5,
                border: '1px solid ' + item.series.color
              }).text(g.tooltip(item)).appendTo("body");
            } else {
              $("#tooltip").remove();
              return previousPoint = null;
            }
          }
        };
      })(g)));
    }
    return _results;
  };
  setTimeout(draw, 10);
}).call(this);
