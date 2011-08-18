root = "{{ url_for('line_by_day', site=site) }}".replace('line_by_day.json', '')

class @Graph
    constructor: (@name)->
    root: root
    url: () ->
        root + @type + '_by_' + @name + ".json"

class @Line extends @Graph
    type: 'line'
    options:
        lines:
             show: true
             fill: true
        points:
            show: true
            fill: true
        grid:
            hoverable: true
        xaxis:
            mode: "time"
            timeformat: "%y-%0m-%0d"
        yaxis: tickDecimals: 0
    data: (response) -> response.series
    tooltip: (item) ->
        y = item.datapoint[1]
        d =  new Date item.datapoint[0]
        y + " " + item.series.label.toLowerCase() + " on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate()

class @Bar extends @Graph
    type: 'bar'
    options:
        bars:
            show: true
            fill: true
        grid:
            hoverable: true
        xaxis:
            min: 0
            max: 23
            ticks: 24
            tickDecimals: 0
        yaxis: tickDecimals: 0
    data: (response) -> [response]
    tooltip: (item) ->
        x = item.datapoint[0]
        y = item.datapoint[1]
        y + " visits at " + x + " h"

class @TimeBar extends @Bar
    options:
        bars:
            show: true
            fill: true
        grid:
            hoverable: true
        xaxis:
            min: 0
            max: 60
            tickDecimals: 0
        yaxis: tickDecimals: 0
    tooltip: (item) ->
        x = item.datapoint[0]
        y = item.datapoint[1]
        y + " visits during between " + x + " and  " + (x+1) + " minutes"

class @Pie extends @Graph
    type: 'pie'
    options:
        grid:
            hoverable: true
        series:
            pie:
                show: true
    data: (response) -> response.list
    tooltip: (item) ->
        p = item.datapoint[0]
        item.series.label + ": " + p.toFixed(1) + "%"
