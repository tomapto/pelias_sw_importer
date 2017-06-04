
var util = require('util'),
    path = require('path'),
    os = require('os'),
    settings = require('pelias-config').generate(),
    split = require('split'),
    through = require('through2'),
    child = require('child_process'),
    exec = "python";


function config(opts){
    if (!opts){
        opts = {};
    }

    // Use datapath setting from your config file
    // @see: github://pelias/config for more info.
    if(!opts.datapath){
        opts.datapath = settings.imports.sw.datapath;
    }

    return opts;
}


function errorHandler( name ){
  return function( data ){
    data.toString('utf8').trim().split('\n').forEach( function( line ){
      console.log( util.format( '[%s]:', name ), line );
    });
  };
}

function createReadStream( opts ){
  var conf = config(opts);
  // var conf = settings.imports.sw.datapath ;
  var flags = [];
  flags.push( path.join(__dirname, "sw2json.py" ) );
  flags.push(  conf.datapath );
  flags.push( "heilongjiang" );

  var proc = child.spawn( exec, flags);

  var decoder = createJsonDecodeStream();
  proc.stdout
    .pipe( split() )
    .pipe( through( function( chunk, enc, next ){
      var str = chunk.toString('utf8'); // convert buffers to strings
      // remove empty lines
      if( 'string' === typeof str && str.length ){
        this.push( str );
      }
      next();
    }))
    .pipe( decoder );

  // print error and exit on decoder pipeline error
  decoder.on( 'error', errorHandler( 'decoder' ) );

  // print error and exit on stderr
  proc.stderr.on( 'data', errorHandler( 'sw2json' ) );

  // terminate the process and pipeline
  decoder.kill = function(){
    proc.kill();
    decoder.end();
  };

  return decoder;
}

function createJsonDecodeStream(){
  return through.obj( function( str, enc, next ){
    try {
      var o = JSON.parse( str );
      if( o ){ this.push( o ); }
    }
    catch( e ){
      this.emit( 'error', e );
    }
    finally {
      next();
    }
  });
}

module.exports.createReadStream = createReadStream;
