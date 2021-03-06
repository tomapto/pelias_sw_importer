var spy = require('through2-spy');
var logger = require('pelias-logger').get('sw-points');
var categoryDefaults = require('../config/category_map');
var path = require('path')

var streams = {};

streams.config = {
  categoryDefaults: categoryDefaults
};

var defaultPath= require('pelias-config').generate().imports.sw;
var conf = { datapath : defaultPath.datapath };

streams.sw2json = require('../sw2json').createReadStream;
streams.docConstructor = require('./document_constructor');
streams.docDenormalizer = require('./denormalizer');
streams.tagMapper = require('./tag_mapper');
streams.adminLookup = require('pelias-wof-admin-lookup').create;
streams.addressExtractor = require('./address_extractor');
streams.deduper = require('./deduper');
streams.categoryMapper = require('./category_mapper');
streams.dbMapper = require('pelias-model').createDocumentMapperStream;
streams.elasticsearch = require('pelias-dbclient');

streams.import = function(){
  streams.sw2json(conf)
    .pipe( streams.docConstructor() )
    .pipe( streams.tagMapper() )
    .pipe( streams.docDenormalizer() )
    .pipe( streams.addressExtractor() )
    .pipe( streams.categoryMapper( categoryDefaults ) )
    .pipe( streams.adminLookup() )
    .pipe( streams.deduper() )
    .pipe( spy.obj(function (doc) {
        logger.info(doc.getGid(), doc.getName('default'), doc.getCentroid());
      })
    )
    .pipe( streams.dbMapper() )
    .pipe( streams.elasticsearch() );
};

module.exports = streams;
