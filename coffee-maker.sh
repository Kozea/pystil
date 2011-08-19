#!/bin/sh
# Use coffee-maker.sh -w to watch for changes
coffee $* --compile pystil/static/js/js.coffee pystil/templates/js/graphs.coffee pystil/static/js/map.coffee
