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
    var angleMode = false;

    var map;
    var geoform;
    var geofile;

    var drawInteraction;
    var selectInteraction;

    var icon = 'images/marker.png';
    var data_base_url;

    function setMode(value) {

        if (currentMode === value)
            return;

        if (value === 'browse') {
            $('button.browse-button', geoform).removeAttr('disabled');
            $('button.edit-button', geoform).attr('disabled', 'disabled');
        }
        else {
            $('button.edit-button', geoform).removeAttr('disabled');
            $('button.browse-button', geoform).attr('disabled', 'disabled');
        }

        currentMode = value;
    }

    function queryHouse(callback) {
        var url = data_base_url + '/config.json';
        var xhr = new XMLHttpRequest();
        xhr.onload = function (e) {
            callback(JSON.parse(xhr.responseText));
        };
        xhr.onerror = function (e) {
            console.log("Get house information failed: " +  e);
        };
        xhr.onabort = function (e) {
            console.log("Get house canceled by the user.");
        };
        xhr.open('GET', url);
        xhr.send(data);
    }

    function uploadFile(url) {
        var data = new FormData(geoform);
        var xhr = new XMLHttpRequest();
        xhr.onload = function (e) {
            console.log("The transfer is complete. server return: " + xhr.responseText);
            var result = JSON.parse(xhr.responseText);
        }
        xhr.upload.addEventListener("progress", function (e) {
            if (e.lengthComputable) {
                var percentComplete = e.loaded / e.total * 100;
                console.log('Upload: ' + percentComplete + '%');
                // $(progress).attr('aria-valuenow', percentComplete).css('width', percentComplete + '%');
                // $(progress).html(formatBytes(e.loaded) + ' / ' + formatBytes(e.total));b
            } else {
                console.log('Unable to compute progress information since the total size is unknown');
            }
        }, false);

        xhr.onerror = function (e) {
            console.log("An error occurred while transferring the file.");
        };
        xhr.onabort = function (e) {
            console.log("The transfer has been canceled by the user.");
        };
        xhr.open('POST', url + '/fileUpload');
        xhr.send(data);
    }

    function removeFeatureApi(name, callback, failCallback) {
        var url = data_base_url + '/' + name;
        var xhr = new XMLHttpRequest();
        xhr.onloadend = function(e) {
            // 204 No Content
            // 404 Not Found (if the resource does not exist)
            // 405 Method Not Allowed (if deleting the resource is not allowed)
            // 500 Internal Server Error
            if (xhr.status != 204) {
                console.log( 'update resource 失败，服务器返回代码：' + xhr.status );
                // failCallback(event);
                return;
            }
            // callback();
            console.log( 'remove house feature OK.');
        };
        xhr.open('DELETE', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        xhr.send('');
    }

    function updateFeatureApi(name, data, callback, failCallback) {
        var url = data_base_url + '/' + name;
        var xhr = new XMLHttpRequest();
        xhr.onloadend = function() {
            if (xhr.status != 204) {
                console.log( 'update resource 失败，服务器返回代码：' + xhr.status );
                return;
            }
            // callback();
            console.log( 'Update house feature OK.');
        };
        xhr.open('PATCH', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        xhr.send( JSON.stringify( data ) );
    }

    function addFeatureApi(data) {
        var url = data_base_url;
        var xhr = new XMLHttpRequest();
        xhr.onloadend = function(e) {

            // 201 Created (Resource has been created successfully)
            // 400 Bad Request (malformed request to the service)
            // 500 Internal Server Error (server fault, can not recover internally)
            if (xhr.status != 201) {
                console.log( 'add house feature 失败，服务器返回代码：' + xhr.status );
                // failCallback(event);
                return;
            }
            var item = JSON.parse( xhr.responseText );
            var newid = item.id;
            // callback();
            console.log( 'Add house feature OK:' + newid);
            uploadFile(newid);
        };
        xhr.open('POST', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        data['@type'] = 'HouseFeature';
        xhr.send( JSON.stringify( data ) );
    }

    $(document).ready(function() {

        data_base_url = document.body.getAttribute('data-base-url');
        geoform = document.getElementById('geofeatureform');
        geofile = document.getElementById('file');

        require([$('body').attr('data-portal-url') + '/++resource++org.snsoffice.base/ol.js'], function (ol) {

            var styleFunction = function (feature, resolution) {
                return new ol.style.Style( {
                    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                        crossOrigin: 'anonymous',
                        src: icon,
                        opacity: 0.6,
                        rotation: feature.get('angle') / 180 * Math.PI,
                    }))
                });
            };

            var selectStyleFunction = function (feature, resolution) {
                return new ol.style.Style( {
                    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                        color: '#8959A8',
                        opacity: 0.8,
                        crossOrigin: 'anonymous',
                        src: icon,
                        rotation: feature.get('angle') / 180 * Math.PI
                    }))
                });
            };

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
                source: source,
                style: styleFunction,
            });

            var fmt = new ol.format.WKT();
            var extent = fmt.readGeometry(geoform.getAttribute('data-geometry')).getExtent();
            var center = ol.extent.getCenter(extent);

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
                    center: center,
                    extent: extent,
                })
            });
            map.getView().fit(extent);

            var element = document.createElement('div');
            element.innerHTML = '<button class="btn btn-success btn-sm"><span class="glyphicon glyphicon-screenshot"></span></button>';
            map.addOverlay(new ol.Overlay({
                id: 'eye',
                element: element,
                positioning: 'center-center',
                stopEvent: true,
            }));

            selectInteraction = new ol.interaction.Select({
                style: selectStyleFunction,
                // condition: ol.events.condition.noModifierKeys,
            });

            selectInteraction.on('select', function (event) {
                if (currentMode === 'edit') {
                    // save result at first
                }

                var preview = document.querySelector('#geo-map .feature-preview');
                preview.innerHTML = '';

                if (event.selected.length) {
                    var selected = event.selected;
                    currentLocation = selected[0].getGeometry().getFirstCoordinate();
                    currentAngle = selected[0].get('angle');
                    originalAngle = currentAngle;
                    originalLocation = currentLocation;

                    var src = selected[0].get('url');
                    if (src) {
                        var img = document.createElement("img");
                        img.src = src;
                        preview.appendChild(img);
                    }
                }
                else {
                    currentLocation = null;
                    currentAngle = null;
                    originalAngle = null;
                    originalLocation = null;
                }
            });
            map.addInteraction(selectInteraction);

            drawInteraction = new ol.interaction.Draw({
                type: 'Point',
                source: source,
                stopClick: true,
            });
            map.addInteraction(drawInteraction);
            drawInteraction.on('drawend', function (e) {
                var selected = selectInteraction.getFeatures();
                if (selected.getLength())
                    source.removeFeature(selected.pop());
                e.feature.set('angle', 0);
                selected.push(e.feature);
            });
            drawInteraction.setActive(false);

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
                var selected = selectInteraction.getFeatures();
                if (ol.events.condition.shiftKeyOnly(evt) && selected.getLength()) {
                    // Change angle of selected feature
                    var coordinate = evt.coordinate;
                    var feature = selected.item(0);
                    var pos = feature.getGeometry().getFirstCoordinate();
                    currentAngle = Math.atan2(coordinate[1] - pos[1], pos[0] - coordinate[0]) * 180 / Math.PI - 90;
                    feature.set('angle', currentAngle);
                    if (currentMode === 'browse')
                        setMode('edit');
                }
                return true;
            });

            geofile.addEventListener('change', function (e) {
                var file = this.files[0];
                var preview = document.querySelector('#geo-map .feature-preview');
                preview.innerHTML = '';
                if (file.type.startsWith('image/')) {
                    var img = document.createElement("img");
                    img.file = file;
                    preview.appendChild(img);

                    var reader = new FileReader();
                    reader.onload = (function(aImg) { return function(e) { aImg.src = e.target.result; }; })(img);
                    reader.readAsDataURL(file);
                    setMode(geofile.getAttribute('data-type'));
                    selectInteraction.setActive(false);
                    drawInteraction.setActive(true);
                    currentLocation = null;
                    currentAngle = null;
                    selectInteraction.getFeatures().clear();
                }
            }, false);

            document.getElementById('form-buttons-add-photo').addEventListener('click', function (e) {
                e.preventDefault();
                geofile.setAttribute('data-type', 'add-photo');
                geofile.click();
            }, false);

            document.getElementById('form-buttons-add-panorama').addEventListener('click', function (e) {
                e.preventDefault();
                geofile.setAttribute('data-type', 'add-panorama');
                geofile.click();
            }, false);

            document.getElementById('form-buttons-remove').addEventListener('click', function (e) {
                e.preventDefault();
                var selected = selectInteraction.getFeatures();
                if (selected.getLength()) {
                    // call restapi to remove feature
                    source.removeFeature(selected.item(0));
                    selected.clear();
                    removeFeatureApi(feature.get('name'));
                }
            }, false);

            document.getElementById('form-buttons-save').addEventListener('click', function (e) {
                var selected = selectInteraction.getFeatures();
                // call restapi to add house feature
                // call fileUpload to upload picture
                if (currentMode === 'add-photo' || currentMode === 'add-panorama') {
                    if (selected.getLength() === 0)
                        return;
                    var pos = feature.getGeometry().getFirstCoordinate();
                    addFeatureApi({
                        title: 'House Feature',
                        phase_type: currentMode === 'add-panorama' ? 'panorama/equirectangular' : 'image/*',
                        geolocation: ol.coordinate.toStringXY(pos, 2),
                        geoangle: feature.get('angle'),
                    });
                    var feature = selected.item(0);
                    console.log('add feature at ' + feature.getGeometry().getFirstCoordinate() + 'and upload picture');
                    drawInteraction.setActive(false);
                    selectInteraction.setActive(true);
                    geofile.value = '';
                }
                // call restapi to update angle and geolocation
                else if (currentMode === 'edit') {
                    var feature = selected.item(0);
                    console.log('set feature ' + feature.get('name') + ': geolocation = ' + currentLocation + ', angle = ' + currentAngle);
                    var pos = feature.getGeometry().getFirstCoordinate();
                    updateFeatureApi(feature.get('name'), {
                        geolocation: ol.coordinate.toStringXY(pos, 2),
                        geoangle: feature.get('angle'),
                    });
                }
                setMode('browse');
            }, false);

            document.getElementById('form-buttons-cancel').addEventListener('click', function (e) {
                var selected = selectInteraction.getFeatures();
                if (currentMode === 'edit') {
                    // restore geolocation and angle
                    if (selected.getLength()) {
                        var feature = selected.item(0);
                        var geom = feature.getGeometry();
                        geom.translate(originalLocation[0] - currentLocation[0], originalLocation[1] - currentLocation[1]);
                        feature.setGeometry(geom);
                        feature.set('angle', originalAngle);
                    }
                    selected = undefined;
                }
                else if (currentMode === 'add-photo' || currentMode === 'add-panorama') {
                    var preview = document.querySelector('#geo-map .feature-preview');
                    preview.innerHTML = '';
                    if (selected.getLength()) {
                        source.removeFeature(selected.pop());
                    }
                    drawInteraction.setActive(false);
                    selectInteraction.setActive(true);
                    geofile.value = '';
                }
                setMode('browse');
            }, false);

            function initHouse(config) {
                var views = config.views === undefined ? [] : config.views;
                for (var i = 0; i < views.length; i ++) {
                    var v = views[i];
                    if (v.type === 'plan') {
                        var imageExtent = fmt.readGeometry(v.geometry).getExtent();
                        var planlayer = new ol.layer.Image( {
                            extent: imageExtent,
                            source: new ol.source.ImageStatic( {
                                crossOrigin: 'anonymous',
                                imageExtent: imageExtent,
                                url: v.url,
                            } )
                        } );
                        map.addLayer(planlayer);
                        break;
                    }
                }
                var features = config.features === undefined ? [] : config.features;
                features.forEach(function(feature){
                    var url = feature.url;
                    var type = feature.type;
                    var pos = feature.geolocation;
                    var angle = feature.geoangle;
                    var title = feature.title;
                    var name = feature.name;

                    var feature = fmt.readFeature('POINT( ' + pos.split(',').join(' ') + ' )');
                    source.addFeature(feature);
                    feature.setProperties({
                        name: name,
                        type: type,
                        angle: angle,
                        title: title,
                    }, true);

                });
            }

            queryHouse(initHouse);

            // var houseFeatures = document.getElementById('house-features');
            // Array.prototype.forEach.call(houseFeatures.querySelectorAll('li'), function (item) {
            //     var url = item.getAttribute('data-url');
            //     var type = item.getAttribute('data-type');
            //     var pos = item.getAttribute('data-location');
            //     var angle = item.getAttribute('data-angle');
            //     var title = item.textContent;

            //     var feature = fmt.readFeature('POINT( ' + pos.split(',').join(' ') + ' )');
            //     source.addFeature(feature);
            //     feature.setProperties({
            //         name: name,
            //         type: type,
            //         angle: angle,
            //         title: title,
            //     }, true);
            // } );

            setMode('browse');
        });

    });
});
