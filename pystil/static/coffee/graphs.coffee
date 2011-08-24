class @Graph extends @Base
    constructor: (@elt) ->
        @datas = []
        super
        @old_index = null
        @elt.bind("plothover", @plothover)

    reply: (response) =>
        super
        $.plot(@elt, @data(response), @options)

    data: (response) ->
        @datas.push(response)
        @datas

    plothover: (event, pos, item) =>
        if item
            index = if item.series.pie.show then item.seriesIndex else item.dataIndex
            if @old_index != index
                @old_index = index
                $("#tooltip").remove()
                $('<div>').attr('id', 'tooltip').css(
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

    data: (response) ->
        @datas = response.list

    tooltip: (item) ->
        p = item.datapoint[0]
        item.series.label + ": " + p.toFixed(1) + "%"
