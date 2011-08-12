(function() {
  window.graphs = function() {
    return [
      {
        name: 'by_hour',
        url: "{{ url_for('visit_by_hour', site=site) }}",
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
        url: "{{ url_for('visit_by_day', site=site) }}",
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
          return response.series;
        },
        tooltip: function(item) {
          var d, y;
          y = item.datapoint[1];
          d = new Date(item.datapoint[0]);
          return y + " " + item.series.label.toLowerCase() + " on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
        }
      }, {
        name: 'by_browser',
        url: "{{ url_for('visit_by_browser', site=site) }}",
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
      }, {
        name: 'by_browser_version',
        url: "{{ url_for('visit_by_browser_version', site=site) }}",
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
      }, {
        name: 'by_platform',
        url: "{{ url_for('visit_by_platform', site=site) }}",
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
      }, {
        name: 'by_host',
        url: "{{ url_for('visit_by_host', site=site) }}",
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
      }, {
        name: 'by_city',
        url: "{{ url_for('visit_by_city', site=site) }}",
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
      }, {
        name: 'by_country',
        url: "{{ url_for('visit_by_country', site=site) }}",
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
      }, {
        name: 'by_referrer',
        url: "{{ url_for('visit_by_referrer', site=site) }}",
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
      }, {
        name: 'by_resolution',
        url: "{{ url_for('visit_by_resolution', site=site) }}",
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
      }, {
        name: 'by_time',
        url: "{{ url_for('visit_by_time', site=site) }}",
        classname: 'pie',
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
            max: 60,
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
          return y + " visits during between " + x + " and  " + (x + 1) + " minutes";
        }
      }
    ];
  };
}).call(this);
