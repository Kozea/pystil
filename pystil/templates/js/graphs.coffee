root = "{{ url_for('visit_by_day', site=site) }}".replace('visit_by_day.json', '')

class Graph
    constructor: (@name)->
        @url = root + 'visit_by_' + name + ".json"

class Line extends Graph
    classname: 'line'
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

class Bars extends Graph
    classname: 'histo'
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

class Pie extends Graph
    classname: 'pie'
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

graphs = []

graph = new Line('day')
graph.tooltip = (item) ->
        y = item.datapoint[1]
        d =  new Date item.datapoint[0]
        y + " " + item.series.label.toLowerCase() + " on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate()
graphs.push(graph)

graph = new Bars('hour')
graph.tooltip = (item) ->
    x = item.datapoint[0]
    y = item.datapoint[1]
    y + " visits at " + x + " h"
graphs.push(graph)

for name in ['browser', 'browser_version', 'platform', 'host', 'city', 'country', 'referrer', 'resolution']
    graphs.push(new Pie(name))

class TimeBars extends Bars
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

graphs.push(new TimeBars('time'))

window.graphs = () ->
    graphs
