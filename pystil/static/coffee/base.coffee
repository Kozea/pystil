class Base
    constructor: (@elt) ->
        @elt.addClass 'loading'

        $.ajax
            url: @url()
            method: 'GET'
            dataType: 'json'
            success: @reply

    reply: (response) =>
        @elt.removeClass('loading')
