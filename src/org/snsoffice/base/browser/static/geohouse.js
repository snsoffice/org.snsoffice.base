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
    'mockup-patterns-relateditems',
    'dropzone',
], function($, Relateditems, Dropzone) {
    'use strict';

    var currentPath = null;

    var roptions = {
        selectableTypes: ["Organization", "Building"], 
        maximumSelectionSize: 1, 
        basePath: "/future/data/villages/",
        closeOnSelect: true,
        mode: 'browse',
    }

    var setupRelatedItems = function($input) {
        // var $input = document.getElementById('form.widgets.village');
        var options = roptions;
        if (options.initialFolder) {
            $input.setAttribute('value', options.initialFolder);
        }
        var ri = new RelatedItems($input, options);
        ri.$el.on('change', function() {
            var result = $(this).select2('data');
            var path = null;
            if (result.length > 0){
                path = result[0].path;
            }
            // self.setPath(path);
            currentPath = path;
        });
        return ri;
    }

    $(document).ready(function() {

        var geolocation = document.getElementById('form-widgets-location');
        var geovillage = document.getElementById('form-widgets-village');

        setupRelatedItems(geovillage);

        require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (ol) {

            var mousePositionControl = new ol.control.MousePosition({
                coordinateFormat: ol.coordinate.createStringXY(4),
                projection: 'EPSG:3857',
                undefinedHTML: '&nbsp;'
            });

            var baseLayer = new ol.layer.Tile({
                source: new ol.source.OSM()
            });

            var source = new ol.source.Vector({wrapX: false});
            var vectorLayer = new ol.layer.Vector({
                source: source
            });

            var fmt = new ol.format.WKT();
            var map = new ol.Map({
                controls: ol.control.defaults({
                    attributionOptions: {
                        collapsible: false
                    }
                }).extend([mousePositionControl]),
                layers: [baseLayer, vectorLayer],
                target: 'geo-map',
                view: new ol.View({
                    enableRotation: false,
                    resolutions: [10, 5, 4, 3, 2, 1, 0.8, 0.5, 0.4, 0.3, 0.2, 0.1],
                })
            });

            var element = document.createElement( 'DIV' );
            element.className = 'ol-geo-locator';
            element.innerHTML = '<span class="glyphicon glyphicon-map-marker"></span>';
            var locator = new ol.Overlay({
                element: element,
                positioning: 'center-center',
                stopEvent: false,
            });
            map.addOverlay( locator );

            map.on('click', function(evt) {
                var coordinate = evt.coordinate;
                locator.setPosition(coordinate);
                return true;
            });

            geovillage.addEventListener('change', function (event) {
                if (currentPath === null)
                    return;
                
            });
            
        });

    });
});
