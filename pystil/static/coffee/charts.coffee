$ ->
    $('embed[src^="/load"]').on('load', ->
        $loading = $ @
        $loading.closest('figure').width($loading.width()).height($loading.height()).css(overflow: 'hidden')
            .append(
                $('<embed>', type: 'image/svg+xml', src: $loading.attr('src').replace('/load', ''))
                .on('load', ->
                    $(this).prev().remove()
                    $(this).closest('figure').attr('style', '')))
    )
