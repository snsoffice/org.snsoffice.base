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
], function($) {
    'use strict';

    $(document).ready(function() {

        require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (ol) {

            var mousePositionControl = new ol.control.MousePosition({
                coordinateFormat: ol.coordinate.createStringXY(4),
                projection: 'EPSG:3857',
                // comment the following two lines to have the mouse position
                // be placed within the map.
                // className: 'custom-mouse-position',
                // target: document.getElementById('geo-mouse-position'),
                undefinedHTML: '&nbsp;'
            });

            var source = new ol.source.Vector({wrapX: false});

            var map = new ol.Map({
                controls: ol.control.defaults({
                    attributionOptions: {
                        collapsible: false
                    }
                }).extend([mousePositionControl]),
                layers: [
                    new ol.layer.Tile({
                        source: new ol.source.OSM()
                    }),
                    new ol.layer.Vector({
                        source: source
                    })
                ],
                target: 'geo-map',
                view: new ol.View({
                    enableRotation: false,
                    resolutions: [10000, 5000, 1200, 300, 76, 20, 5, 1, 0.1],
                    center: [12119628.52, 4055386.0],
                    zoom: 2
                })
            });

            var element = document.createElement( 'DIV' );
            element.innerHTML = '<span class="glyphicon glyphicon-map-marker"></span>';

            var locator = new ol.Overlay({
                id: 'locator',
                element: element,
                positioning: 'bottom-center',
                stopEvent: false,
            });
            
            map.addOverlay( locator );

            var drawInteraction = new ol.interaction.Draw({
                source: source,
                type: 'Circle',
                condition: ol.events.condition.shiftKeyOnly,
                geometryFunction: ol.interaction.Draw.createBox()
            });
            map.addInteraction(drawInteraction);

            drawInteraction.on('drawstart', function (e) {
                source.clear();
            });

            drawInteraction.on('drawend', function (e) {
                var extent = e.feature.getGeometry().getExtent();
                var element = document.getElementById('form-widgets-IGeoFeature-geoextent');
                if (element)
                    element.value = extent.join(',');
            });

            map.on('click', function(evt) {
                var coordinate = evt.coordinate;
                var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(
                    coordinate, 'EPSG:3857', 'EPSG:4326'));                
                locator.setPosition(coordinate);
                var element = document.getElementById('form-widgets-IGeoFeature-geolocation');
                if (element)
                    element.value = coordinate.join(',');
                return true;
            });
            
        });

    });
});
