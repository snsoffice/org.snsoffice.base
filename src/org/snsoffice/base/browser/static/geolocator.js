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

    function getArrayFromString(s) {
        var a = [];
        s.split(',').forEach( function (v) {
            a.push(parseFloat(v));
        } );
        return a;
    }

    function getStringFromArray(arr, opt_fractionDigits) {
        var result = [];
        arr.forEach( function (v) {
            result.push(v.toFixed(opt_fractionDigits));
        });
        return result;
    }

    $(document).ready(function() {

        var locationinput = document.getElementById('form-widgets-IGeoFeature-coordinate');
        var geometryinput = document.getElementById('form-widgets-geometry');
        var geotypeinput = document.getElementById('form-widgets-geotype');

        require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (ol) {


            var georesult = document.getElementById('form-widgets-georesult');
            var controls = document.getElementById('geo-form-controls');
            var footer = document.querySelector('.plone-modal-footer');
            if (footer && controls) {
                controls.remove();
                footer.appendChild(controls);
                georesult = document.getElementById('form-widgets-georesult');
            }

            if (typeof geometryinput === 'undefined') {
                geotypeinput.setAttribute('disabled', 'disabled');
            }

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
            var baseLayer = new ol.layer.Tile({
                source: new ol.source.OSM()
            });
            var vectorLayer = new ol.layer.Vector({
                source: source
            });

            var overviewControl = new ol.control.OverviewMap({
                layers: [baseLayer],
            });

            var center = locationinput.value.trim() === '' ? [12119628.52, 4055386.0] : getArrayFromString(locationinput.value);
            var map = new ol.Map({
                controls: ol.control.defaults({
                    attributionOptions: {
                        collapsible: false
                    }
                }).extend([mousePositionControl, overviewControl]),
                layers: [baseLayer, vectorLayer],
                target: 'geo-map',
                view: new ol.View({
                    enableRotation: false,
                    resolutions: [10000, 5000, 1200, 300, 76, 20, 10, 5, 4, 3, 2, 1, 0.8, 0.5, 0.4, 0.1],
                    center: center,
                    resolution: 10,
                })
            });

            var element = document.createElement( 'DIV' );
            element.className = 'ol-geo-locator';
            element.innerHTML = '<span class="glyphicon glyphicon-map-marker"></span>';

            var locator = new ol.Overlay({
                id: 'locator',
                element: element,
                positioning: 'center-center',
                stopEvent: false,
            });

            map.addOverlay( locator );

            // var modifyInteraction = new ol.interaction.Modify({source: source});
            // map.addInteraction(modifyInteraction);

            var drawInteraction;

            function addInteraction(shape) {
                if (shape === 'box') {
                    drawInteraction = new ol.interaction.Draw({
                        source: source,
                        type: 'Circle',
                        stopClick: true,
                        // condition: ol.events.condition.shiftKeyOnly,
                        freehandCondition: ol.events.condition.never,
                        geometryFunction: ol.interaction.Draw.createBox()
                    });
                }
                else {
                    drawInteraction = new ol.interaction.Draw({
                        source: source,
                        stopClick: true,
                        type: 'Polygon', // Point
                        freehandCondition: ol.events.condition.never,
                    });
                }
                map.addInteraction(drawInteraction);

                drawInteraction.on('drawstart', function (e) {
                    source.clear();
                });

                drawInteraction.on('drawend', function (e) {
                    if (typeof geoextent !== 'undefined') {
                        geoextent.value = getStringFromArray(e.feature.getGeometry().getExtent(), 2);
                    }
                    if (typeof geometryinput !== 'undefined') {
                        var fmt = new ol.format.WKT();
                        georesult.value = fmt.writeGeometry(e.feature.getGeometry(), { decimals: 2 });
                        geometryinput.value = georesult.value;
                    }
                });
            }

            map.on('click', function(evt) {
                var coordinate = evt.coordinate;
                var hdms = ol.coordinate.toStringHDMS(ol.proj.transform(
                    coordinate, 'EPSG:3857', 'EPSG:4326'));
                locator.setPosition(coordinate);
                georesult.value = ol.coordinate.toStringXY(coordinate, 2);
                locationinput.value = georesult.value;
                return true;
            });

            geotypeinput.addEventListener('change', function (event) {
                if (!event.target.value)
                    return;

                if (typeof drawInteraction !== 'undefined') {
                    map.removeInteraction(drawInteraction);
                    drawInteraction = undefined;
                }

                var v = event.target.value;
                if (v === 'box' || v === 'polygon') {
                    addInteraction(v);
                }
            }, false);

            if (locationinput.value.trim() !== '') {
                locator.setPosition(map.getView().getCenter());
            }

            if (geometryinput !== undefined && geometryinput.value !== undefined && geometryinput.value.trim() !== '') {
                // var extent = getArrayFromString(geoextent.value);
                // var feature = new ol.Feature({
                //     geometry: ol.geom.Polygon.fromExtent(extent)
                // });
                var fmt = new ol.format.WKT();
                var feature = fmt.readFeature(geometryinput.value);
                var style = new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: [255, 255, 255, 0.5]
                    }),
                    stroke: new ol.style.Stroke({
                        color: [0, 153, 255, 1],
                        width: 1.0,
                    }),
                });
                feature.setStyle(style);
                source.addFeature(feature);

                var extent = feature.getGeometry().getExtent();
                map.getView().fit(extent, {
                    size: [100, 100],
                    constrainResolution: false,
                    duration: 500,
                });
            }

        });

    });
});
