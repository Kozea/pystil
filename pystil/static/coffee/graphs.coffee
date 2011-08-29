class @Graph extends @Base
    constructor: (@elt) ->
        @data = []
        @plotable = true
        super
        @old_index = null
        @elt.bind("plothover", @plothover)

    reply: (response) =>
        super
        if response.list
            for serie in response.list
                @data.push(serie)
        else
            @data.push(response)
        @plot()

    clear: () ->
        super
        @data = []

    plot: () ->
        $.plot(@elt, @data, @options)

    plothover: (event, pos, item) =>
        if item
            index = if item.series.pie.show then item.seriesIndex else item.dataIndex
            if @old_index != index
                @old_index = index
                $("#tooltip").remove()
                $('<div>').attr('id', 'tooltip').css(
                    position: 'absolute'
                    padding: '2px'
                    'background-color': 'white'
                    'border-radius': '10px 0 0 0'
                    opacity: 0.80
                    top: pos.pageY + 5,
                    left: pos.pageX + 5,
                    border: '1px solid ' + item.series.color
                ).text(@tooltip item).appendTo("body")
        else
            $("#tooltip").remove()
            @old_index = null


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
            labelAngle: 50
        yaxis: tickDecimals: 0


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

    tooltip: (item) ->
        x = item.datapoint[0]
        y = item.datapoint[1]
        y + " visits at " + x + " h"


class @Time extends @Bar
    options:
        bars:
            show: true
            fill: true
        grid:
            hoverable: true
        xaxis:
            ticks: [[0, "0"], [1, "1s"], [2, "2s"], [3, "5s"], [4, "10s"], [5, "20s"]
                    [6, "30s"], [7, "1min"], [8, "2min"], [9, "5min"], [10, "10min"]
                    [11, "10+ min"]]
        yaxis: tickDecimals: 0

    tooltip: (item) ->
        x = item.datapoint[0]
        y = item.datapoint[1]
        y + " visits"


class @Pie extends @Graph
    type: 'pie'

    options:
        grid:
            hoverable: true
        series:
            pie:
                show: true

    tooltip: (item) ->
        p = item.datapoint[0]
        item.series.label + ": " + p.toFixed(1) + "%"
