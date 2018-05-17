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
    'resource-plone-app-jquerytools-js'
], function($, ol) {
    'use strict';

    $(document).ready(function() {

        $('button.edit_geofeature').on('click', function () {
            require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (ol) {
                alert('ol is ' + ol);
            });
        });

    });
});
