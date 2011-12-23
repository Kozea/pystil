fs     = require 'fs'
{exec} = require 'child_process'
util   = require 'util'
uglify = require 'uglify-js'

root = './pystil/static'
coffee_dir = "#{root}/coffee"
js_file = "#{root}/js/all.js"
js_with_deps_file = "#{root}/js/all-deps.js"
pystil_coffee_file = 'tracker.coffee'
pystil_js_file = "#{root}/js/tracker.js"
pystil_min_file = "#{root}/js/pystil.js"
min_file = "#{root}/js/js.js"
all_coffee_file = "#{root}/coffee/all.coffee"
coffee_opts = "--output #{root}/js/ --compile #{all_coffee_file} "

coffee_files = [
    'base'
    'map'
    'graphs'
    'last'
    'top'
    'tabs'
    'main'
]

deps_files = [
    'jquery.min'
    'jquery-ui.min'
    'jquery.flot'
    'jquery.flot.pie'
    'curvedLines'
    'all'
]

debug = false

task 'watch-debug', 'Watch coffee files and build changes', ->
    debug = true
    invoke 'watch'


task 'watch', 'Watch coffee files and build changes', ->
    invoke 'build'
    invoke 'build:tracker'
    util.log "Watching for changes in #{coffee_dir}"
    for file in coffee_files then do (file) ->
        fs.watchFile "#{coffee_dir}/#{file}.coffee", (curr, prev) ->
            if +curr.mtime isnt +prev.mtime
                util.log "Saw change in #{coffee_dir}/#{file}.coffee"
                invoke 'build'
                util.log "Watching for changes in #{coffee_dir}"

    fs.watchFile "#{coffee_dir}/#{pystil_coffee_file}", (curr, prev) ->
        if +curr.mtime isnt +prev.mtime
            util.log "Saw change in #{coffee_dir}/#{pystil_coffee_file}"
            invoke 'build:tracker'
            util.log "Watching for changes in #{coffee_dir}"


task 'build:tracker', 'Build the tracker file to js', ->
    util.log "Building tracker"
    exec "coffee --output #{root}/js/ --compile #{coffee_dir}/#{pystil_coffee_file} ",
        (err, stdout, stderr) ->
            handleError(err) if err
            util.log "Compiled #{pystil_js_file}"
            invoke 'uglify:tracker'


task 'uglify:tracker', 'Minify and obfuscate the tracker', ->
    util.log "Minifying #{pystil_js_file}"
    jsp = uglify.parser
    pro = uglify.uglify
    util.log "jsp #{jsp}"
    fs.readFile pystil_js_file, 'utf8', (err, fileContents) ->
        ast = jsp.parse fileContents  # parse code and get the initial AST
        ast = pro.ast_mangle ast # get a new AST with mangled names
        ast = pro.ast_squeeze ast # get an AST with compression optimizations
        final_code = pro.gen_code ast # compressed code here
        fs.writeFile pystil_min_file, final_code
        util.log "Uglified #{pystil_js_file} (#{fileContents.length} chars) to #{pystil_min_file} (#{final_code.length} chars)"


task 'build', 'Build a single js file from coffee files', ->
    util.log "Building #{js_file}"
    appContents = new Array remaining = coffee_files.length
    util.log "Appending #{coffee_files.length} files to #{all_coffee_file}"

    for file, index in coffee_files then do (file, index) ->
        util.log "Reading #{file}"
        fs.readFile "#{coffee_dir}/#{file}.coffee",
            'utf8',
            (err, fileContents) ->
                handleError(err) if err
                appContents[index] = fileContents
                util.log "Added [#{index + 1}] #{file}.coffee"
                if --remaining is 0
                    util.log "All file read"
                    process()
    process = ->
        util.log "Writing #{all_coffee_file}..."
        fs.writeFile all_coffee_file,
            appContents.join('\n\n'),
            'utf8',
            (err) ->
                handleError(err) if err
                util.log "Running coffee..."
                exec "coffee #{coffee_opts}", (err, stdout, stderr) ->
                    handleError(err) if err
                    util.log "Compiled #{js_file}"
                    util.log "Removing #{all_coffee_file}"
                    fs.unlink all_coffee_file, (err) ->
                        handleError(err) if err
                        invoke 'deps'

task 'deps', 'Include deps files', ->
    util.log "Appending deps to #{js_with_deps_file}"
    appContents = new Array remaining = deps_files.length
    util.log "Appending #{deps_files.length} files to #{js_with_deps_file}"

    for file, index in deps_files then do (file, index) ->
        util.log "Reading #{file}"
        fs.readFile "#{root}/js/#{file}.js",
            'utf8',
            (err, fileContents) ->
                handleError(err) if err
                appContents[index] = fileContents
                util.log "Added [#{index + 1}] #{file}.js"
                if --remaining is 0
                    util.log "All file read"
                    process()
    process = ->
        util.log "Writing #{js_with_deps_file}..."
        fs.writeFile js_with_deps_file,
            appContents.join('\n\n'),
            'utf8',
            (err) ->
                handleError(err) if err
                invoke 'uglify'

task 'uglify', 'Minify and obfuscate', ->
    if debug
        util.log "Moving #{js_with_deps_file} to #{min_file}"
        fs.rename js_with_deps_file, min_file, (err, fileContents) -> util.log "Done"
        return

    util.log "Minifying #{js_with_deps_file}"
    jsp = uglify.parser
    pro = uglify.uglify

    fs.readFile js_with_deps_file, 'utf8', (err, fileContents) ->
        ast = jsp.parse fileContents  # parse code and get the initial AST
        ast = pro.ast_mangle ast # get a new AST with mangled names
        ast = pro.ast_squeeze ast # get an AST with compression optimizations
        final_code = pro.gen_code ast # compressed code here
        fs.writeFile min_file, final_code
        util.log "Uglified #{js_with_deps_file} (#{fileContents.length} chars) to #{min_file} (#{final_code.length} chars)"

handleError = (error) ->
    exec "notify-send 'Cake error:' '#{error}'"
    throw error
