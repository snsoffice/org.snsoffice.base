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

    var map;
    var fmt;
    var source;

    var portal_url = document.body.getAttribute('data-portal-url');
    var currentPath = null;
    var currentBuilding = null;

    var roptions = {
        selectableTypes: ["Organization", "Building"],
        maximumSelectionSize: 1,
        rootPath: "/data/villages",
        closeOnSelect: true,
        vocabularyUrl: "getVocabulary?name=plone.app.vocabularies.Catalog",
    }

    var setOrganization;
    var setupRelatedItems = function($input) {
        // var $input = document.getElementById('form.widgets.village');
        var options = roptions;
        if (options.initialFolder) {
            $input.attr('value', options.initialFolder);
        }
        var ri = new Relateditems($input, options);
        ri.$el.on('change', function() {
            var result = $(this).select2('data');
            var path = null;
            if (result.length > 0){
                path = result[0].path;
            }
            currentPath = path;
            setOrganization(path);
        });
        return ri;
    }

    $(document).ready(function() {

        var geolocation = document.getElementById('form-widgets-location');
        var geovillage = document.getElementById('form-widgets-village');

        setupRelatedItems($(geovillage));

        require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (ol) {

            fmt = new ol.format.WKT();

            var mousePositionControl = new ol.control.MousePosition({
                coordinateFormat: ol.coordinate.createStringXY(4),
                projection: 'EPSG:3857',
                undefinedHTML: '&nbsp;'
            });

            var baseLayer = new ol.layer.Tile({
                source: new ol.source.OSM()
            });
            
            function buildingStyleFunction( feature, resolution ) {
                return new ol.style.Style( {
                    fill: new ol.style.Fill( {
                        color: 'rgba(255, 255, 255, 0.3)',
                    } ),
                    stroke: new ol.style.Stroke( {
                        color: 'rgba(0, 0, 255, 0.3)',
                        width: 1,
                    } ),
                    text: new ol.style.Text( {
                        text: feature.get( 'title' ),
                        scale: 2.0,
                        offsetY: 20,
                        padding: [ 2, 2, 2, 2 ],
                    } )
                } );
            };

            source = new ol.source.Vector({wrapX: false});
            var vectorLayer = new ol.layer.Vector({
                source: source,
                style: buildingStyleFunction,
            });

            var center = [12119628.52, 4055386.0];

            map = new ol.Map({
                controls: ol.control.defaults({
                    attributionOptions: {
                        collapsible: false
                    }
                }).extend([mousePositionControl]),
                layers: [baseLayer, vectorLayer],
                target: 'geo-map',
                view: new ol.View({
                    enableRotation: false,
                    resolutions: [1200, 10, 5, 4, 3, 2, 1, 0.8, 0.5, 0.4, 0.3, 0.2, 0.1],
                    center: center,
                    resolution: 1200,
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
                var features = map.getFeaturesAtPixel(evt.pixel);
                if (features.length > 0) {
                    currentBuilding = features[0].getId();
                    locator.setPosition(evt.coordinate);
                    geolocation.value = ol.coordinate.toStringXY(evt.coordinate, 2);
                }
                return true;
            });

            geovillage.addEventListener('change', function (event) {
                if (currentPath === null)
                    return;

            });

            setOrganization = function (path) {
                var url = portal_url + path;
                var request = new XMLHttpRequest();

                request.onerror = function ( event ) {
                    console.log('Something is wrong');
                };

                request.onloadend = function() {

                    if (request.status != 200) {
                        console.log( 'Get ' + url + ' return error: ' + request.status );
                        return;
                    }
                    var data = JSON.parse( request.responseText );
                    source.clear();
                    
                    var items = data.children;
                    for (var i=0; i < items.length; i ++) {
                        var feature = fmt.readFeature(items[i].geometry);
                        feature.setId(items[i].name);
                        feature.set('title', items[i].title, true);
                        source.addFeature(feature);
                    }

                    map.getView().fit(fmt.readGeometry(data.geometry), {
                        constrainResolution: false,
                        duration: 500,
                    });
                };
                request.open('GET', url, true);
                request.send();

        });

    });
});
