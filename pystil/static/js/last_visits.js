(function() {
  var last_visits;
  last_visits = function() {
    var stamp, success, update;
    stamp = new Date().getTime();
    update = function() {
      return $.ajax({
        url: location.href + "*/" + stamp + "/last_visits.json",
        method: 'GET',
        dataType: 'json',
        success: success
      });
    };
    success = function(response) {
      var visit, _i, _len, _ref;
      _ref = response.list;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        visit = _ref[_i];
        $("#last-visits tbody").prepend($('<tr>').append($('<td>').text(visit.host)).append($('<td>').text(visit.ip)).append($('<td>').text(visit.country)).append($('<td>').text(visit.city)).append($('<td>').text(visit.page)).append($('<td>').text(visit.referrer)));
      }
      stamp = new Date().getTime();
      return setTimeout(update, 2000);
    };
    return $.ajax({
      url: location.href + "/*/" + stamp + "/last_visits.json",
      method: 'GET',
      dataType: 'json',
      success: success
    });
  };
  $(last_visits);
}).call(this);
