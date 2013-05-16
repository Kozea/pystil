// Generated by CoffeeScript 1.6.2
(function() {
  var commands;

  commands = {
    INFO: function(m) {
      return console.log(m);
    },
    VISIT: function(m) {
      var $line;

      if ($('table.last').size()) {
        $line = $(m);
        $line.addClass('active');
        $line.addClass('recent');
        $('table.last tbody').prepend($line);
        setTimeout((function() {
          return $line.removeClass('recent');
        }), 500);
      }
      $('header h1 a').addClass('pulse');
      return setTimeout((function() {
        return $('header h1 a').removeClass('pulse');
      }), 75);
    },
    EXIT: function(id) {
      id = parseInt(id);
      return $("table.last tr[data-visit-id=" + id + "]").removeClass('active');
    }
  };

  $(function() {
    var ws;

    window.ws = ws = new WebSocket("ws://" + location.host + "/ws");
    ws.onopen = function() {
      return console.log('Websocket opened', arguments);
    };
    ws.onerror = function() {
      return console.log('Websocket errored', arguments);
    };
    return ws.onmessage = function(evt) {
      var cmd, data, message, pipe;

      message = evt.data;
      pipe = message.indexOf('|');
      if (pipe > -1) {
        cmd = message.substr(0, pipe);
        data = message.substr(pipe + 1);
        return commands[cmd](data);
      }
    };
  });

}).call(this);

/*
//@ sourceMappingURL=websocket.map
*/
