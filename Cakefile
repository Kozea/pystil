fs     = require 'fs'
{exec} = require 'child_process'
util   = require 'util'
uglify = require 'uglify-js'

coffee_dir = './pystil/static/coffee/'
js_dir = './pystil/static/'
js_file = './pystil/static/all.js'
min_file = './pystil/static/min.js'
all_coffee_file = './pystil/static/all.coffee'

coffee_opts = "--output #{js_dir} --compile #{all_coffee_file} "

coffee_files = [
    'base'
    'map'
    'graphs'
    'last_visits'
    'main'
]

task 'watch', 'Watch coffee files and build changes', ->
    invoke 'build'
    util.log "Watching for changes in #{coffee_dir}"

    for file in coffee_files then do (file) ->
        fs.watchFile "#{coffee_dir}/#{file}.coffee", (curr, prev) ->
            if +curr.mtime isnt +prev.mtime
                util.log "Saw change in #{coffee_dir}/#{file}.coffee"
                invoke 'build'

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
                util.log "Done"
                util.log "Running coffee..."
                exec "coffee #{coffee_opts}", (err, stdout, stderr) ->
                    handleError(err) if err
                    util.log "Compiled #{js_file}"
                    util.log "Removing #{all_coffee_file}"
                    fs.unlink all_coffee_file, (err) ->
                        handleError(err) if err
                        invoke 'uglify'

task 'uglify', 'Minify and obfuscate', ->
    util.log "Minifying #{js_file}"
    jsp = uglify.parser
    pro = uglify.uglify

    fs.readFile js_file, 'utf8', (err, fileContents) ->
        ast = jsp.parse fileContents  # parse code and get the initial AST
        ast = pro.ast_mangle ast # get a new AST with mangled names
        ast = pro.ast_squeeze ast # get an AST with compression optimizations
        final_code = pro.gen_code ast # compressed code here

        fs.writeFile min_file, final_code

        util.log "Uglified #{js_file} to #{min_file} (#{final_code.length} chars)"

handleError = (error) ->
    throw error
