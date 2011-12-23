class @Top extends @Base
    type: 'top'

    constructor: (@elt) ->
        super
        @plotable = true
        @elt.append(table = $('<table>')
            .append($('<thead>')
                .append($('<tr>')
                    .append($('<th>').text("Site"))
                    .append($('<th>').text("Visits")))))
        table.append(@tbody = $('<tbody>'))

    reply: (response) =>
        super
        @update(response)

    clear: () ->
        super
        @tbody.find('tr').remove()

    update: (response) =>
        for host in response.list
            @tbody.append($('<tr>')
                .append($('<td>').text(host.key))
                .append($('<td>').text(host.count)))
