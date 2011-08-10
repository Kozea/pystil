(function() {
  window.graphs = [
    {
      name: 'by_hour',
      url: "{{ url_for('visit_by_hour') }}",
      classname: 'histo',
      options: {
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
      },
      data: function(response) {
        return [response];
      },
      tooltip: function(item) {
        var x, y;
        x = item.datapoint[0];
        y = item.datapoint[1];
        return y + " visits at " + x + " h";
      }
    }, {
      name: 'by_day',
      url: "{{ url_for('visit_by_day') }}",
      classname: 'line',
      options: {
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
      },
      data: function(response) {
        return [response];
      },
      tooltip: function(item) {
        var d, y;
        y = item.datapoint[1];
        d = new Date(item.datapoint[0]);
        return y + " visits on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
      }
    }, {
      name: 'by_browser',
      url: "{{ url_for('visit_by_browser') }}",
      classname: 'pie',
      options: {
        grid: {
          hoverable: true
        },
        series: {
          pie: {
            show: true
          }
        }
      },
      data: function(response) {
        return response.list;
      },
      tooltip: function(item) {
        var p;
        p = item.datapoint[0];
        return item.series.label + ": " + p.toFixed(1) + "%";
      }
    }
  ];
}).call(this);
