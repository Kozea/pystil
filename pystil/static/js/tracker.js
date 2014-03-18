// Generated by CoffeeScript 1.6.3
(function() {
  var make_query, send, tracker,
    _this = this;

  make_query = function(track) {
    var k, v;
    return ((function() {
      var _results;
      _results = [];
      for (k in track) {
        v = track[k];
        _results.push("" + k + "=" + (escape(v)));
      }
      return _results;
    })()).join('&');
  };

  send = function(query, time) {
    var im;
    im = new Image();
    return im.src = "%spystil-" + time + ".gif?" + query;
  };

  tracker = function() {
    var c, e, l, now, previous_unload, time, track, uuid;
    now = new Date();
    time = now.getTime();
    c = l = null;
    uuid = "%s";
    try {
      c = _this.document.cookie.match('pystil=[0-9]+\\$(.+)');
      try {
        l = _this.document.cookie.match('pystil=([0-9]+)');
      } catch (_error) {
        e = _error;
        0;
      }
      if ((c != null ? c.length : void 0) > 1 && c[1] !== 'undefined') {
        uuid = c[1];
      }
      _this.document.cookie = "pystil=" + time + "$" + uuid + "; path=/";
    } catch (_error) {
      e = _error;
      0;
    }
    track = {
      _: uuid,
      s: _this.screen.width + 'x' + _this.screen.height,
      r: _this.document.referrer,
      u: "" + _this.location.protocol + "//" + _this.location.host,
      k: _this.location.hostname,
      p: _this.location.pathname,
      h: _this.location.hash,
      q: _this.location.search,
      d: 'o',
      z: -now.getTimezoneOffset(),
      l: (l || [])[1],
      i: navigator.language || navigator.userLanguage || navigator.browserLanguage
    };
    if (track.r.indexOf(track.u) > -1) {
      track.r = track.r.replace(track.u, '');
    }
    send(make_query(track), time);
    previous_unload = _this.onunload ? _this.onunload : function() {};
    return _this.onunload = function() {
      var retrack;
      retrack = {
        _: uuid,
        d: 'c',
        t: new Date().getTime() - time
      };
      send(make_query(retrack), time);
      return previous_unload();
    };
  };

  this.setTimeout((function() {
    var e, inner;
    try {
      return tracker();
    } catch (_error) {
      e = _error;
      try {
        return send('d=e&r=' + e.toString(), new Date().getTime());
      } catch (_error) {
        inner = _error;
        return 0;
      }
    }
  }), 10);

}).call(this);
