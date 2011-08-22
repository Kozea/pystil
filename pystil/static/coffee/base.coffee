class Base
    data_type: 'json'
    constructor: (@elt) ->
        @elt.addClass 'loading'
        $.ajax
            url: @url()
            method: 'GET'
            dataType: @data_type
            success: @reply

    reply: (response) =>
        @elt.removeClass('loading')

    root: "/" + location.pathname.split("/")[1] + "/"
