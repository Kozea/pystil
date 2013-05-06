$ ->
    $('embed[data-site]').on('load', ->
        $loading = $(@)
        d = (what) -> $loading.attr("data-#{what}")
        $loading.closest('figure').width($loading.width()).height($loading.height()).css(overflow: 'hidden')
            .append(
                $('<embed>', type: 'image/svg+xml', src: "/data/#{d('site')}/#{d('type')}/#{d('criteria')}.svg")
                .on('load', ->
                    $(this).prev().remove()
                    $(this).closest('figure').attr('style', '')))
    )
