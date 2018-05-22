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

    var originalLocation = null;
    var originalAngle = null;
    var currentLocation = null;
    var currentAngle = null;
    var currentMode = null;

    var geoform;
    var selected;

    function setMode(value) {

        if (currentMode === value)
            return;

        originalLocation = null;
        originalAngle = null;
        currentLocation = null;
        currentAngle = null;

        if (value === 'browse') {
            $('button.browse-button', geoform).removeAttr('disabled');
            $('button.edit-button', geoform).attr('disabled', 'disabled');
        }
        else{
            $('button.edit-button', geoform).removeAttr('disabled');
            $('button.browse-button', geoform).attr('disabled', 'disabled');
        }

        currentMode = value;
    }

    $(document).ready(function() {

        geoform = document.getElementById('geofeatureform');
        var geofile = document.getElementById('form-widgets-file');

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
            var extent = fmt.readGeometry(geometry.value).getExtent();
            var center = ol.extent.getCenter(extent);

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
                    center: center,
                    resolution: 1,
                })
            });

            var element = document.createElement( 'DIV' );
            element.className = 'ol-geo-locator';
            element.innerHTML = '<span class="glyphicon glyphicon-screenshot"></span>';

            var locator = new ol.Overlay({
                element: element,
                positioning: 'center-center',
                stopEvent: false,
            });

            map.addOverlay( locator );

            var selectInteraction;
            selectInteraction = new ol.interaction.Select();

            selectInteraction.on('select', function (event) {
                if (event.selected.length) {
                    selected = event.selected;                   
                    currentLocation = selected[0].getGeometry().getFirstCoordinate();
                    currentAngle = feature.get('angle');
                    originalAngle = currentAngle;
                    originalLocation = currentLocation;
                    locator.setPosition(currentLocation);
                }
                else
                    selected = undefined;
            });
            map.addInteraction(selectInteraction);

            var translateInteraction = new ol.interaction.Translate({
                features: selectInteraction.getFeatures()
            });
            translateInteraction.on('translateend', function (event) {
                var features = event.features;
                var coordinate = event.coordinate;
                setMode('edit');
                currentLocation = coordinate;
            });
            map.addInteraction(translateInteraction);

            map.on('click', function(evt) {
                var coordinate = evt.coordinate;
                if (currentMode === 'new-panorama' || currentMode === 'new-photo') {
                }
                return true;
            });

            geofile.addEventListener('change', function (e) {
                if (currentMode === 'edit') {
                }
                else if (currentMode === 'add-panorama') {
                }
                if (currentMode === 'add-photo') {
                }                
            }, false);

            document.getElementById('form-buttons-add-photo').addEventListener('click', function (e) {
                e.preventDefault();
                setMode('add-photo');
                geofile.click();
            }, false);

            document.getElementById('form-buttons-add-panorama').addEventListener('click', function (e) {
                e.preventDefault();
                setMode('add-panorama');
                geofile.click();
            }, false);

            document.getElementById('form-buttons-remove').addEventListener('click', function (e) {
                e.preventDefault();
                if (selected && selected.length > 0) {
                }
            }, false);

            document.getElementById('form-buttons-save').addEventListener('click', function (e) {
                setMode('browse');
            }, false);

            document.getElementById('form-buttons-cancel').addEventListener('click', function (e) {
                setMode('browse');
            }, false);

        });

    });
});
