@tabs = () =>
    $.fn.extend
        tabshow: (fn) ->
            @each (i, e) ->
                if fn
                    $.event.add e, "tabshow", fn, null
                else
                    evt = $.Event "tabshow", target: e
                    $.event.trigger "tabshow", evt, e, false

    $('.tabs').each (i, elt) ->
        $tab = $ '.tab', elt
        $lnks = $ 'ul li a', elt
        $lnks.first().addClass 'active'
        $tab.first().tabshow().show()

        $tab.not($tab.first()).hide()
        $lnks.click (evt) ->
            $lnks.removeClass 'active'
            $(@).addClass 'active'
            $tab.hide()
            $("##{@href.split('#')[1]}").tabshow().show()
            false
