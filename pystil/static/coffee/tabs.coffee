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
        $lnks = $ 'ul li a', elt
        $tab = $ '.tab', elt

        $lnks.first().addClass 'active'
        $tab.first().addClass('active').tabshow().css left: 0

        $tab.not($tab.first()).css left: window.innerWidth

        $lnks.click (evt) ->
            $old_tab_active = $ '.tab.active', elt
            $new_tab_active = $ "##{@href.split('#')[1]}"
            $old_lnk_active = $ 'ul li a.active', elt
            $new_lnk_active = $ @

            $old_tab_active.removeClass 'active'
            $old_lnk_active.removeClass 'active'

            $new_tab_active.addClass 'active'
            $new_lnk_active.addClass 'active'

            $tab.each (i, e) ->
                sign =  i - $tab.index($new_tab_active)
                $(e).css left: sign * window.innerWidth
            $new_tab_active.tabshow()
            false
