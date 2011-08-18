(function() {
  var root;
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  };
  root = "{{ url_for('line_by_day', site=site) }}".replace('line_by_day.json', '');
  this.Graph = (function() {
    function Graph(name) {
      this.name = name;
    }
    Graph.prototype.root = root;
    Graph.prototype.url = function() {
      return root + this.type + '_by_' + this.name + ".json";
    };
    return Graph;
  })();
  this.Line = (function() {
    __extends(Line, this.Graph);
    function Line() {
      Line.__super__.constructor.apply(this, arguments);
    }
    Line.prototype.type = 'line';
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
    Line.prototype.tooltip = function(item) {
      var d, y;
      y = item.datapoint[1];
      d = new Date(item.datapoint[0]);
      return y + " " + item.series.label.toLowerCase() + " on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
    };
    return Line;
  }).call(this);
  this.Bar = (function() {
    __extends(Bar, this.Graph);
    function Bar() {
      Bar.__super__.constructor.apply(this, arguments);
    }
    Bar.prototype.type = 'bar';
    Bar.prototype.options = {
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
    Bar.prototype.data = function(response) {
      return [response];
    };
    Bar.prototype.tooltip = function(item) {
      var x, y;
      x = item.datapoint[0];
      y = item.datapoint[1];
      return y + " visits at " + x + " h";
    };
    return Bar;
  }).call(this);
  this.TimeBar = (function() {
    __extends(TimeBar, this.Bar);
    function TimeBar() {
      TimeBar.__super__.constructor.apply(this, arguments);
    }
    TimeBar.prototype.options = {
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
    TimeBar.prototype.tooltip = function(item) {
      var x, y;
      x = item.datapoint[0];
      y = item.datapoint[1];
      return y + " visits during between " + x + " and  " + (x + 1) + " minutes";
    };
    return TimeBar;
  }).call(this);
  this.Pie = (function() {
    __extends(Pie, this.Graph);
    function Pie() {
      Pie.__super__.constructor.apply(this, arguments);
    }
    Pie.prototype.type = 'pie';
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
  }).call(this);
}).call(this);
