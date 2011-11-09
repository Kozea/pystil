$.fn.extend
    tabshow: (fn) ->
        @each (i, e) ->
            if fn
                $.event.add e, "tabshow", fn, null
            else
                evt = $.Event "tabshow", target: e
                $.event.trigger "tabshow", evt, e, false

@tabs = () =>
    $('.tabs').each (i, elt) ->
        $tab = $ '.tab', elt
        $lnks = $ 'ul li a', elt
        $lnks.first().addClass 'active'
        $tab.first().tabshow().css 'left': 0
        $tab.not($tab.first()).css 'left': -window.innerWidth

        $lnks.click (evt) ->
            $lnks.removeClass 'active'
            $(@).addClass 'active'
            $tab.css 'left': -window.innerWidth
            $("##{@href.split('#')[1]}").tabshow().css 'left': 0
            false
