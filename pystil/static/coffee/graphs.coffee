bgColors = ["rgba(255, 255, 255, 0)", "rgba(255, 255, 255, 1)"]
pie_colors = [
    "#4c7ca5" # 4
    "#4ca5a2" # 5
    "#4ca55d" # 6
    "#eac516" # 7
    "#ea9316" # 8
    "#bb6120" # 9
    "#bb2020" # 10
    "#af3151" # 0
    "#a54ca1" # 1
    "#854ca5" # 2
    "#504ca5" # 3
    ]

colors = [
    "#504ca5" # 3
    "#4c7ca5" # 4
    "#4ca5a2" # 5
    ]
legendOpacity = 0.1

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
        legend:
            backgroundOpacity: legendOpacity
        colors: colors
        series:
            curvedLines:
                active: true
                show: true
        points:
            show: true
        xaxis:
            mode: "time"
            timeformat: "%y-%0m-%0d"
            labelAngle: 50
        yaxis:
            tickDecimals: 0
        grid:
            hoverable: true
            backgroundColor:
                colors: bgColors

    tooltip: (item) ->
        y = item.datapoint[1]
        d =  new Date item.datapoint[0]
        y + " " + item.series.label.toLowerCase() + " on " + d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate()


class @Bar extends @Graph
    type: 'bar'

    options:
        legend:
            backgroundOpacity: legendOpacity
        colors: colors
        bars:
            show: true
            fill: true
        xaxis:
            min: 0
            max: 24
            ticks: 25
            tickDecimals: 0
        yaxis:
            tickDecimals: 0
        grid:
            hoverable: true
            backgroundColor:
                colors: bgColors

    tooltip: (item) ->
        x = item.datapoint[0]
        y = item.datapoint[1]
        y + " visits at " + x + " h"


class @Time extends @Bar
    options:
        legend:
            backgroundOpacity: legendOpacity
        colors: colors
        bars:
            show: true
            fill: true
        xaxis:
            ticks: [[0, "0"], [1, "1s"], [2, "2s"], [3, "5s"], [4, "10s"], [5, "20s"]
                    [6, "30s"], [7, "1min"], [8, "2min"], [9, "5min"], [10, "10min"]
                    [11, "10+ min"]]
        yaxis:
            tickDecimals: 0
        grid:
            hoverable: true
            backgroundColor:
                colors: bgColors

    tooltip: (item) ->
        x = item.datapoint[0]
        y = item.datapoint[1]
        y + " visits"


class @Pie extends @Graph
    type: 'pie'

    options:
        legend:
            backgroundOpacity: legendOpacity
        colors: pie_colors
        grid:
            hoverable: true
        series:
            pie:
                show: true

    tooltip: (item) ->
        p = item.datapoint[0]
        item.series.label + ": " + p.toFixed(1) + "%"
