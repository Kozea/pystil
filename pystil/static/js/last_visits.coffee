last_visits = () ->
    stamp = new Date().getTime()
    update = () ->
        $.ajax
            url: location.href + "*/" + stamp + "/last_visits.json"
            method: 'GET'
            dataType: 'json'
            success: success

    success = (response) ->
        for visit in response.list
            $("#last-visits tbody")
                .prepend($('<tr>')
                    .append($('<td>').text(visit.host))
                    .append($('<td>').text(visit.ip))
                    .append($('<td>').text(visit.country))
                    .append($('<td>').text(visit.city))
                    .append($('<td>').text(visit.page))
                    .append($('<td>').text(visit.referrer)))
        stamp = new Date().getTime()
        setTimeout(update, 2000)

    $.ajax
        url: location.href + "/*/" + stamp + "/last_visits.json"
        method: 'GET'
        dataType: 'json'
        success: success


$ last_visits
