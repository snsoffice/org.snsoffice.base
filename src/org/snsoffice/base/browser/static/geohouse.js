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

    var ol;

    var map;
    var fmt;
    var source;

    var currentPath;
    var currentBuilding;
    var currentBuildingTitle;
    var currentFloor;
    var currentLocation;

    var geoform;
    var houselocation;
    var portal_url;

    var patmodal;

    var roptions = {
        selectableTypes: ["Organization"],
        maximumSelectionSize: 1,
        rootPath: "/data/villages",
        basePath: "/data/villages",
        initialFolder: "/data/villages",
        closeOnSelect: true,
        vocabularyUrl: "getVocabulary?name=plone.app.vocabularies.Catalog",
    }

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
        });
        return ri;
    }

    var formatBytes = function(bytes) {
        var kb = Math.round(bytes / 1024);
        if (kb < 1024) {
            return kb + ' KiB';
        }
        var mb = Math.round(kb / 1024);
        if (mb < 1024) {
            return mb + ' MB';
        }
        return Math.round(mb / 1024) + ' GB';
    };

    var importHouse = function () {
        // ajax post request
        var url = portal_url + currentPath + '/' + currentBuilding;
        var data = new FormData(geoform);
        data.append('form.widgets.building', currentPath + '/' + currentBuilding);
        data.append('form.widgets.geolocation', currentLocation);
        data.append('form.widgets.floor', currentFloor);

        var $progress = $('.progress-bar-success', geoform);
        var xhr = new XMLHttpRequest();
        xhr.onload = function (e) {
            console.log("The transfer is complete. server return: " + xhr.responseText);
            var result = JSON.parse(xhr.responseText);
            if (result.url)
                window.location.href = result.url;
        };
        xhr.upload.addEventListener("progress", function (e) {
            if (e.lengthComputable) {
                var percentComplete = e.loaded / e.total * 100;
                $progress.attr('aria-valuenow', percentComplete).css('width', percentComplete + '%');
                $progress.html(formatBytes(e.loaded) + ' / ' + formatBytes(e.total));b
            } else {
                // Unable to compute progress information since the total size is unknown
            }
        }, false);
        xhr.onerror = function (e) {
            console.log("An error occurred while transferring the file.");
        };
        xhr.onabort = function (e) {
            console.log("The transfer has been canceled by the user.");
        };
        xhr.open('POST', url + '/import-house');
        xhr.send(data);
    };

    var setHouseLocation = function () {
        houselocation.value = currentBuildingTitle + ( currentFloor ? ' - ' + currentFloor + '层' : '' ) + ' ( ' + currentLocation + ' )';
    };

    var initMap = function () {

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
                resolutions: [20000, 2000, 200, 20, 10, 5, 4, 3, 2, 1, 0.8, 0.5, 0.4, 0.3, 0.2, 0.1],
                center: center,
                resolution: 20000,
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
                currentFloor = patmodal.querySelector('#modal-floor').value.trim();
                currentLocation = ol.coordinate.toStringXY(evt.coordinate, 2);
                currentBuildingTitle = features[0].getTitle();

                locator.setPosition(evt.coordinate);
                patmodal.querySelector('#modal-geolocation').value = currentLocation;

                setHouseLocation();
            }
            return true;
        });

    };

    var initPatModal = function () {

        patmodal = document.querySelector('.plone-modal-wrapper');

        var footer = patmodal.querySelector('.plone-modal-footer');
        var controls = patmodal.querySelector('.row.locatorControls');
        if (footer && controls) {
            controls.remove();
            footer.appendChild(controls);
        }

        if (!!currentPath)
            return;


        var building = patmodal.getElementById('modal-building');
        building.addEventListener('change', function (e) {
            var feature = source.getFeatureById(e.target.value);
            currentBuilding = e.target.value;
            currentBuildingTitle = feature.getTitle();
            setHouseLocation();
        }, false);

        patmodal.getElementById('modal-floor').addEventListener('change', function (e) {
            currentFloor = e.target.value.trim();
            setHouseLocation();
        }, false);

        var url = portal_url + currentPath + '/config.json';
        var xhr = new XMLHttpRequest();

        xhr.onloadend = function() {

            if (xhr.status != 200) {
                console.log( 'Server return ' + xhr.status + ' when get data from ' + url);
                return;
            }
            var data = JSON.parse( xhr.responseText );
            source.clear();

            var items = data.children;
            var options = [];
            for (var i=0; i < items.length; i ++) {
                var name = items[i].name;
                var title = items[i].title;
                var feature = fmt.readFeature(items[i].geometry);
                feature.setId(name);
                feature.set('title', title, true);
                source.addFeature(feature);
                options.push('<option value="' + name + '">' + title + '</option>');
            }

            building.innerHTML = options.join('');

            map.getView().fit(fmt.readGeometry(data.geometry), {
                constrainResolution: false,
                duration: 500,
            });
        };
        xhr.open('GET', url, true);
        xhr.send();
    };

    function validateFields() {
        if (geovillage.value.trim() === '')
            $('#formfield-form-widgets-village').addClass('error');
        if (geotitle.value.trim() === '')
            $('#formfield-form-widgets-title').addClass('error');
        return currentPath === null || currentBuilding === null || geolocation.value.trim() === '' || geotitle.value.trim() === '';
    }

    document.getElementById('form-buttons-import').addEventListener('click', function (e) {
        e.preventDefault();
        $('#form-widgets-file', geoform).click();
        return true;
    }, false);

    document.getElementById('form-buttons-new').addEventListener('click', function (e) {
        e.preventDefault();
        if (validateFields())
            return;

        var url = portal_url + currentPath + '/' + currentBuilding;
        var xhr = new XMLHttpRequest();
        xhr.onloadend = function(e) {
            // 201 Created (Resource has been created successfully)
            // 400 Bad Request (malformed request to the service)
            // 500 Internal Server Error (server fault, can not recover internally)
            if (xhr.status != 201) {
                console.log( '添加房子失败，服务器返回代码：' + xhr.status );
                return;
            }
            window.location.href = xhr.response.url;
        };
        xhr.open('POST', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        data = {
            '@type': 'House',
            'title': geoform.querySelector('#form-widgets-title').value,
            'description': geoform.querySelector('#form-widgets-description').value,
            'area': geoform.querySelector('#form-widgets-area').value,
            'house_type': geoform.querySelector('#form-widgets-house_type').value,
            'floor': currentFloor,
        };
        xhr.send( JSON.stringify( data ) );
    }, false);

    $(document).ready(function() {

        geoform = document.getElementById('geoform');
        houselocation = geoform.querySelector('input#form-widgets-location');
        portal_url = document.body.getAttribute('data-portal-url');

        $('.pat-plone-modal', geoform).on('show.plone-modal.patterns', function (e) {
            initPatModal();
        });

        setupRelatedItems($('input#form-widgets-village'));

        geoform.querySelector('#form-widgets-file').addEventListener('change', importHouse, false);

        require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (olx) {
            ol = olx;
            initMap();
        });

    });
});
