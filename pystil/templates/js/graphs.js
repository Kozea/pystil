(function() {
  var Bars, Graph, Line, Pie, TimeBars, graph, graphs, name, root, _i, _len, _ref;
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  root = "{{ url_for('visit_by_day', site=site) }}".replace('visit_by_day.json', '');
  Graph = (function() {
    function Graph(name) {
      this.name = name;
      this.url = root + 'visit_by_' + name + ".json";
    }
    return Graph;
  })();
  Line = (function() {
    __extends(Line, Graph);
    function Line() {
      Line.__super__.constructor.apply(this, arguments);
    }
    Line.prototype.classname = 'line';
    Line.prototype.options = {
      lines: {
        show: true,
        fill: true
      },
      points: {
        show: true,
        fill: true
      },
      grid: {
        hoverable: true
      },
      xaxis: {
        mode: "time",
        timeformat: "%y-%0m-%0d"
      },
      yaxis: {
        tickDecimals: 0
      }
    };
    Line.prototype.data = function(response) {
      return response.series;
    };
    return Line;
  })();
  Bars = (function() {
    __extends(Bars, Graph);
    function Bars() {
      Bars.__super__.constructor.apply(this, arguments);
    }
    Bars.prototype.classname = 'histo';
    Bars.prototype.options = {
      bars: {
        show: true,
        fill: true
      },
      grid: {
        hoverable: true
      },
      xaxis: {
        min: 0,
        max: 23,
        ticks: 24,
        tickDecimals: 0
      },
      yaxis: {
        tickDecimals: 0
      }
    };
    Bars.prototype.data = function(response) {
      return [response];
    };
    return Bars;
  })();
  Pie = (function() {
    __extends(Pie, Graph);
    function Pie() {
      Pie.__super__.constructor.apply(this, arguments);
    }
    Pie.prototype.classname = 'pie';
    Pie.prototype.options = {
      grid: {
        hoverable: true
      },
      series: {
        pie: {
          show: true
        }
      }
    };
    Pie.prototype.data = function(response) {
      return response.list;
    };
    Pie.prototype.tooltip = function(item) {
      var p;
      p = item.datapoint[0];
      return item.series.label + ": " + p.toFixed(1) + "%";
    };
    return Pie;
  })();
  graphs = [];
  graph = new Line('day');
  graph.tooltip = function(item) {
    var d, y;
    y = item.datapoint[1];
    d = new Date(item.datapoint[0]);
    return y + " " + item.series.label.toLowerCase() + " on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
  };
  graphs.push(graph);
  graph = new Bars('hour');
  graph.tooltip = function(item) {
    var x, y;
    x = item.datapoint[0];
    y = item.datapoint[1];
    return y + " visits at " + x + " h";
  };
  graphs.push(graph);
  _ref = ['browser', 'browser_version', 'platform', 'host', 'city', 'country', 'referrer', 'resolution'];
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    name = _ref[_i];
    graphs.push(new Pie(name));
  }
  TimeBars = (function() {
    __extends(TimeBars, Bars);
    function TimeBars() {
      TimeBars.__super__.constructor.apply(this, arguments);
    }
    TimeBars.prototype.options = {
      bars: {
        show: true,
        fill: true
      },
      grid: {
        hoverable: true
      },
      xaxis: {
        min: 0,
        max: 60,
        tickDecimals: 0
      },
      yaxis: {
        tickDecimals: 0
      }
    };
    TimeBars.prototype.tooltip = function(item) {
      var x, y;
      x = item.datapoint[0];
      y = item.datapoint[1];
      return y + " visits during between " + x + " and  " + (x + 1) + " minutes";
    };
    return TimeBars;
  })();
  graphs.push(new TimeBars('time'));
  window.graphs = function() {
    return graphs;
  };
}).call(this);
