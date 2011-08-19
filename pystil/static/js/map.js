(function() {
  var map;
  map = function() {
    var success;
    $("body").append($('<div>').attr('id', 'tooltip').css({
      position: 'absolute',
      display: 'none'
    }));
    $(".country").mouseover(function(e) {
      return $('#tooltip').css({
        top: e.pageY + 10 + 'px',
        left: e.pageX + 10 + 'px',
        display: 'block'
      }).text($('title', e.currentTarget).text());
    });
    $(".country").mouseout(function(e) {
      return $('#tooltip').css({
        display: 'none'
      });
    });
    success = function(response) {
      var country, _i, _len, _ref, _results;
      _ref = response.list;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        country = _ref[_i];
        _results.push($("#" + country.key.split("$")[1].toLowerCase()).css({
          fill: 'rgba(0, 0, 255, ' + ((country.count / response.max) * 0.7 + 0.2) + ')'
        }).prepend($('<title>').text(country.key.split("$")[0].toLowerCase() + ": " + country.count)));
      }
      return _results;
    };
    return $.ajax({
      url: location.href + "_by_visit.json",
      method: 'GET',
      dataType: 'json',
      success: success
    });
  };
  $(map);
}).call(this);
