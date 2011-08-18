(function() {
  var draw;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  draw = __bind(function() {
    var $elt, elt, g, previousPoint, success, _i, _len, _ref, _results;
    _ref = $(".graph");
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      elt = _ref[_i];
      $elt = $(elt);
      if ($elt.hasClass("pie")) {
        g = new this.Pie(elt.id);
      } else if ($elt.hasClass("line")) {
        g = new this.Line(elt.id);
      } else if ($elt.hasClass("bar")) {
        if ($elt.hasClass("time")) {
          g = new this.TimeBar(elt.id);
        } else {
          g = new this.Bar(elt.id);
        }
      }
      $elt.addClass('loading');
      success = (function(g, $elt) {
        return function(response) {
          $elt.removeClass('loading');
          return $.plot($elt, g.data(response), g.options);
        };
      })(g, $elt);
      $.ajax({
        url: g.url(),
        method: 'GET',
        dataType: 'json',
        success: success
      });
      previousPoint = null;
      _results.push($elt.bind("plothover", (function(g) {
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
            }
          } else {
            $("#tooltip").remove();
            return previousPoint = null;
          }
        };
      })(g)));
    }
    return _results;
  }, this);
  $(draw);
}).call(this);
