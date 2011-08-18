// Copyright (C) 2011 by Florian Mounier, Kozea
// This file is part of pystil, licensed under a 3-clause BSD license.
(function () {
    try {
    window.setTimeout(function () {
        var h = function(e, n, h) { var c = function() {}; if (e[n]) {c = e[n]} e[n] = function (e) {h(e); c(e);}};
	    var w = window, l = w.location, d = w.document, s = w.screen, r = {}, i = (d.cookie.match('pystil=[0-9]+\\$(.+)') || [])[1] || "%s", q = '_=' + i, z = new w.Date(), t = z.getTime();
        var g = function (q) {new w.Image().src = "%s" + "pystil-" + t + ".gif?" + q;};
        var j = function (a, r) {var q = a; for (var k in r) {if(r[k]) {q += '&' + k + "=" + escape(r[k]);}} return q;};
        r.s = s.width + 'x' + s.height;
        r.r = d.referrer;
        r.u = l.protocol + '//' + l.host;
        r.k = l.hostname;
        r.p = l.pathname;
        r.h = l.hash;
        r.q = l.search;
        r.d = "o";
        r.z = -z.getTimezoneOffset();
        r.l = (d.cookie.match('pystil=([0-9]+)') || [])[1];
        d.cookie = "pystil="+t+"$"+i+"; path=/"
        if(r.r.indexOf(r.u) > -1) r.r = r.r.replace(r.u, '');
        g(j(q, r));
        h(w, 'onunload', function () {
            var r = {};
            r.d = "c"
            r.t = new w.Date().getTime() - t;
            g(j(q, r));
        });
    }, 10);
    } catch (e) {}
})();
