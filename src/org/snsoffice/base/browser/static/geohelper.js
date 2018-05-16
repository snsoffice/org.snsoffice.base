/* global require, window */
/* jshint quotmark: false */

if(require === undefined){
    require = function(reqs, torun){  // jshint ignore:line
        'use strict';
        return torun(window.jQuery);
    };
}

require([ // jshint ignore:line
    'jquery',
    'ol.js',
    'resource-plone-app-jquerytools-js'
], function($, ol) {
    'use strict';

    $(document).ready(function() {
        console.log('ol is ' + ol);
    });
});
