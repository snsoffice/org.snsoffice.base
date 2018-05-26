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

    var originalLocation;
    var originalAngle;
    var modified;

    var map;
    var selectInteraction;

    var geoform;
    var geofile;

    var marker_icon_url;
    var data_base_url;
    var data_portal_url;

    var houseFeatures;
    var progress;

    function clearSelectedImage() {
        Array.prototype.forEach.call(houseFeatures.querySelectorAll('img.selected'), function (img) {
            img.className = '';
        });
    }

    function isSelectedImage(img) {
        return img.className === 'selected';
    }

    function scrollIntoView( element ) {
        houseFeatures.scrollLeft = element.offsetLeft;
    }

    function setModified( value ) {

        if ( modified === value )
            return;

        if ( value ) {
            $('button.edit-button', geoform).removeAttr('disabled');
            $('button.browse-button', geoform).attr('disabled', 'disabled');
        }
        else {
            $('button.browse-button', geoform).removeAttr('disabled');
            $('button.edit-button', geoform).attr('disabled', 'disabled');
        }

        modified = value;
    }

    function uploadFile( url, callback, failCallback ) {

        var data = new FormData(geoform);
        var xhr = new XMLHttpRequest();

        xhr.onloadend = function (e) {
            $(progress).hide();
        }

        xhr.onload = function (e) {
            console.log("The transfer is complete. server return: " + xhr.responseText);            
        }
        xhr.upload.addEventListener("progress", function (e) {
            if (e.lengthComputable) {
                var percentComplete = e.loaded / e.total * 100;
                console.log('Upload: ' + percentComplete + '%');
                progress.firstElementChild.textContent = percentComplete + '%';
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

        $(progress).show();
        xhr.open('POST', url + '/fileUpload');
        xhr.send(data);
    }

    function addFeatureApiRest( data, callback, failCallback ) {

        // Debug
        if (false && data) {
            console.log('New feature: ' + data);
            callback( {
                id: 'feature-new-1',
                geolocation: data.geolocation,
                geoangle: data.geoangle,
            } );
            return true;
        }

        var url = data_base_url;
        var xhr = new XMLHttpRequest();
        xhr.onloadend = function(e) {

            // 201 Created (Resource has been created successfully)
            // 400 Bad Request (malformed request to the service)
            // 500 Internal Server Error (server fault, can not recover internally)
            if (xhr.status != 201) {
                console.log( 'add house feature 失败，服务器返回代码：' + xhr.status );
                failCallback(event);
                return;
            }
            var item = xhr.response;
            var newid = item.id;
            callback( item );
            console.log( 'Add house feature OK:' + newid);
            uploadFile( item['@id'] );
        };
        xhr.open('POST', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        data['@type'] = 'HouseFeature';
        xhr.send( JSON.stringify( data ) );
    }

    function addFeatureApi( data, callback, failCallback ) {

        var url = data_base_url + '/new-house-feature';
        var xhr = new XMLHttpRequest();
        xhr.onloadend = function(e) {

            if (xhr.status != 200) {
                console.log( 'add house feature 失败，服务器返回代码：' + xhr.status );
                failCallback(event);
                return;
            }
            var item = xhr.response;
            callback( item );
            console.log( 'Add house feature OK.');
        };

        var formData = new FormData(geoform);
        formData.append('form.widgets.angle', data.geoangle);
        formData.append('form.widgets.location', data.geolocation);
        formData.append('form.widgets.type', data.phase_type);
        formData.append('form.widgets.source', data.source);

        xhr.open('POST', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        xhr.send( formData );
    }

    function removeFeatureApi(name, callback, failCallback) {
        var url = data_base_url + '/' + name;
        // Debug
        if (url) {
            console.log('Remove ' + url);
            // return true;
        }
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
        // Debug
        if (url) {
            console.log('Update ' + url);
            // return true;
        }

        var xhr = new XMLHttpRequest();
        xhr.onloadend = function() {
            if (xhr.status != 204) {
                console.log( 'update resource 失败，服务器返回代码：' + xhr.status );
            if (typeof failCallback === 'function')
                failCallback();
                return;
            }
            if (typeof callback === 'function')
                callback();
            console.log( 'Update house feature OK.');
        };
        xhr.open('PATCH', url, true);
        xhr.setRequestHeader( 'Accept', 'application/json' );
        xhr.setRequestHeader( 'Content-Type', 'application/json' );
        xhr.responseType = 'json';
        xhr.send( JSON.stringify( data ) );
    }

    $(document).ready(function() {

        data_base_url = document.body.getAttribute('data-base-url');
        data_portal_url = document.body.getAttribute('data-portal-url');
        marker_icon_url = data_portal_url + '/++resource++org.snsoffice.base/marker.png';
        geoform = document.getElementById('geofeatureform');
        geofile = geoform.querySelector('input#form-widget-file');
        houseFeatures = document.getElementById('house-features');
        progress = document.createElement('DIV');
        progress.innerHTML = '<div class="plone-loader"><div class="loader"/></div>';
        document.body.appendChild(progress);

        require([data_portal_url + '/++resource++org.snsoffice.base/ol.js'], function (ol) {

            function saveFeature( feature ) {
                var name = feature.getId();
                var data = {
                    geolocation: ol.coordinate.toStringXY( feature.getGeometry().getFirstCoordinate(), 2 ),
                    angle: feature.get('angle'),
                };
                var oldValue = [ originalLocation, originalAngle ];
                updateFeatureApi( name, data, null, function () {
                    restoreFeature( feature, oldValue );
                } );
            }

            function restoreFeature( feature, oldValue ) {
                var geom = feature.getGeometry();
                var currentLocation = feature.getGeometry().getFirstCoordinate();
                geom.translate(oldValue[0][0] - currentLocation[0], oldValue[0][1] - currentLocation[1]);
                feature.setGeometry(geom);
                feature.set('angle', oldValue[1]);
            }

            var styleFunction = function (feature, resolution) {
                return new ol.style.Style( {
                    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                        crossOrigin: 'anonymous',
                        src: marker_icon_url,
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
                        src: marker_icon_url,
                        rotation: feature.get('angle') / 180 * Math.PI
                    }))
                });
            };

            var baseLayer = new ol.layer.Tile({
                source: new ol.source.OSM()
            });

            var source = new ol.source.Vector({wrapX: false});
            var vectorLayer = new ol.layer.Vector({
                source: source,
                style: styleFunction,
            });

            var fmt = new ol.format.WKT();
            var extent = fmt.readGeometry(document.getElementById('geo-map').getAttribute('data-geometry')).getExtent();
            var center = ol.extent.getCenter(extent);

            map = new ol.Map({
                controls: ol.control.defaults({
                    attributionOptions: {
                        collapsible: false
                    }
                }).extend([]),
                layers: [baseLayer],
                target: 'geo-map',
                view: new ol.View({
                    enableRotation: false,
                    center: center,
                    extent: extent,
                })
            });
            map.getView().fit(extent);

            var houseViews = document.getElementById('house-views');
            if (houseViews) {
                var planview = houseViews.querySelector('li');
                if (planview) {
                    var planlayer = new ol.layer.Image( {
                        extent: extent,
                        source: new ol.source.ImageStatic( {
                            crossOrigin: 'anonymous',
                            imageExtent: extent,
                            url: planview.getAttribute('data-url'),
                        } )
                    } );
                    map.addLayer(planlayer);
                }
            }

            map.addLayer(vectorLayer);

            selectInteraction = new ol.interaction.Select({
                style: selectStyleFunction,
            });

            selectInteraction.on('select', function (event) {
                // save result at first
                if (modified) {
                    var img = houseFeatures.querySelector('img.selected');
                    if (img) {
                        var feature = source.getFeatureById(img.getAttribute('data-name'));
                        if (feature) {
                            saveFeature(feature);
                        }
                    }
                    setModified(false);
                }

                clearSelectedImage();

                if (event.selected.length) {
                    var feature = event.selected[0];
                    originalAngle = feature.get('angle');
                    originalLocation = feature.getGeometry().getFirstCoordinate();;

                    var name = feature.getId();
                    Array.prototype.forEach.call(houseFeatures.querySelectorAll('img[data-name="' + name + '"]'), function (img) {
                        img.className = 'selected';
                        scrollIntoView(img);
                    });
                }
                else {
                    originalAngle = null;
                    originalLocation = null;
                }
            });
            map.addInteraction(selectInteraction);

            // drawInteraction = new ol.interaction.Draw({
            //     type: 'Point',
            //     source: source,
            //     stopClick: true,
            // });
            // map.addInteraction(drawInteraction);
            // drawInteraction.on('drawend', function (e) {
            //     var selected = selectInteraction.getFeatures();
            //     selected.forEach(function(feature) {
            //         source.removeFeature(feature);
            //     });
            //     selected.clear();

            //     e.feature.set('angle', 0);
            //     selected.push(e.feature);
            // });
            // drawInteraction.setActive(false);

            var translateInteraction = new ol.interaction.Translate({
                features: selectInteraction.getFeatures()
            });
            translateInteraction.on('translateend', function (event) {
                setModified(true);
            });
            map.addInteraction(translateInteraction);

            map.on('click', function(evt) {
                var selected = selectInteraction.getFeatures();
                if (ol.events.condition.shiftKeyOnly(evt) && selected.getLength()) {
                    // Change angle of selected feature
                    var coordinate = evt.coordinate;
                    var feature = selected.item(0);
                    var origin = feature.getGeometry().getFirstCoordinate();
                    var angle = Math.atan2(coordinate[1] - origin[1], origin[0] - coordinate[0]) * 180 / Math.PI - 90;
                    feature.set('angle', angle);
                    setModified(true);
                }
                return true;
            });

            function onFeatureAdded(data) {
                var feature = fmt.readFeature('POINT( ' + data.geolocation.split(',').join(' ') + ' )');
                feature.setId(data.id);
                feature.set('angle', data.geoangle, true);
                source.addFeature(feature);

                selectInteraction.getFeatures().push(feature);
                geofile.value = '';

                var img = houseFeatures.querySelector('img.selected');
                img.setAttribute('data-name', data.id);
            }

            function onFeatureAddFailed() {
                selectInteraction.getFeatures().clear();
                var img = houseFeatures.querySelector('img.selected');
                if (img)
                    img.remove();
            }

            geofile.addEventListener( 'change', function ( e ) {

                clearSelectedImage();
                selectInteraction.getFeatures().clear();

                var file = this.files[ 0 ];
                if ( file.type.startsWith( 'image/') ) {

                    var preview = document.createElement('DIV');
                    preview.className = 'preview';

                    var img = document.createElement('IMG');
                    img.file = file;
                    img.className = 'selected';

                    var span = document.createElement('SPAN');
                    span.className = 'glyphicon glyphicon-remove-circle';

                    preview.appendChild(img);
                    preview.appendChild(span);
                    houseFeatures.firstElementChild.appendChild(preview);

                    var reader = new FileReader();
                    reader.onload = ( function( aImg ) {
                        return function ( e ) {
                            aImg.src = e.target.result;
                            scrollIntoView(aImg);
                        };
                    } )( img );
                    reader.readAsDataURL( file );

                    var currentLocation = map.getView().getCenter();
                    var currentAngle = 0;

                    var data = {
                        phase_type: geofile.getAttribute( 'data-type' ),
                        geolocation: ol.coordinate.toStringXY(currentLocation, 2),
                        geoangle: currentAngle,
                        source: file.name,
                    };
                    addFeatureApi( data, onFeatureAdded, onFeatureAddFailed );
                }
            }, false);

            document.getElementById('form-buttons-add-photo').addEventListener('click', function (e) {
                e.preventDefault();
                geofile.setAttribute('data-type', 'photo');
                geofile.click();
            }, false);

            document.getElementById('form-buttons-add-panorama').addEventListener('click', function (e) {
                e.preventDefault();
                geofile.setAttribute('data-type', 'panorama');
                geofile.click();
            }, false);

            document.getElementById('form-buttons-remove').addEventListener('click', function (e) {
                e.preventDefault();
                var selected = selectInteraction.getFeatures();
                if (selected.getLength()) {
                    // call restapi to remove feature
                    var feature = selected.item(0);
                    removeFeatureApi(feature.getId());
                    source.removeFeature(feature);
                    selected.clear();
                    houseFeatures.querySelector('img.selected').remove();
                }
                if (modified)
                    setModified(false);
            }, false);

            document.getElementById('form-buttons-save').addEventListener('click', function (e) {
                var selected = selectInteraction.getFeatures();
                // call restapi to update angle and geolocation
                if (selected.getLength()) {
                    var feature = selected.item(0);
                    var pos = feature.getGeometry().getFirstCoordinate();
                    updateFeatureApi(feature.getId(), {
                        geolocation: ol.coordinate.toStringXY(pos, 2),
                        geoangle: feature.get('angle'),
                    });
                }
                setModified(false);
            }, false);

            document.getElementById('form-buttons-cancel').addEventListener('click', function (e) {
                var selected = selectInteraction.getFeatures();
                // restore geolocation and angle
                if (selected.getLength()) {
                    restoreFeature( selected.item(0), [ originalLocation, originalAngle ] );
                }
                setModified(false);
            }, false);

            houseFeatures.addEventListener( 'click', function ( e ) {

                if (e.target.tagName === 'SPAN') {
                    var preview = e.target.parentElement;
                    var img = preview.firstElementChild;
                    if (img) {
                        var feature = source.getFeatureById(img.getAttribute('data-name'));
                        if (feature) {
                            removeFeatureApi(feature.getId());
                            source.removeFeature(feature);
                            if (isSelectedImage(img)) {
                                selectInteraction.getFeatures().clear();
                                if (modified)
                                    setModified(false);
                            }
                        }
                    }
                    preview.remove();
                    return;
                }

                var img = e.target;
                var name = img.getAttribute('data-name');
                if (isSelectedImage(img))
                    return;

                // save result at first if modified
                if (modified) {
                    if (selectInteraction.getFeatures().getLength()) {
                        saveFeature(selectInteraction.getFeatures().item(0));
                    }
                    setModified(false);
                }

                clearSelectedImage();
                selectInteraction.getFeatures().clear();
                if ( name ) {
                    var feature = source.getFeatureById( name );
                    if ( feature ) {
                        selectInteraction.getFeatures().push( feature );
                        img.className = 'selected';
                        originalAngle = feature.get('angle');
                        originalLocation = feature.getGeometry().getFirstCoordinate();
                    }
                }

            }, false );

            Array.prototype.forEach.call(houseFeatures.querySelectorAll('IMG'), function (item) {
                var name = item.getAttribute('data-name');
                var type = item.getAttribute('data-type');
                var pos = item.getAttribute('data-location');
                var angle = item.getAttribute('data-angle');

                var feature = fmt.readFeature('POINT( ' + pos.split(',').join(' ') + ' )');
                feature.setId(name);
                feature.setProperties({
                    type: type,
                    angle: angle,
                }, true);
                source.addFeature(feature);
            } );

            setModified(false);
        });

    });
});
