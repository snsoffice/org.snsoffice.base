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
    'qiniu.min.js'
], function($) {
    'use strict';

    function get_upload_token(key) {
        var element = document.getElementById('resources-key-prefix');
        var key = element.value;
        var request = new XMLHttpRequest();
        var url = '/ifuture/' + key + '/getUploadToken' ;
        var params = 'portal_type=Organization&path=/future/organizations';

        request.onerror = function ( event ) {
            utils.warning( '获取云服务器上传凭证 ' + url + '时出现了错误!' );
        };

        request.onloadend = function() {

            if (request.status != 200) {
                utils.warning( '获取云服务器上传凭证 ' + url + '失败，服务器返回代码：' + request.status );
                return;
            }
            callback( JSON.parse( request.responseText ).token );
        };
        request.open('GET', url + '?' + params, true);
        request.send();
    }

    function remove_resource_file(path, key) {
        var request = new XMLHttpRequest();
        var url = path + '/removeResource' ;
        var params = 'key=' + key;

        request.onerror = function ( event ) {
            utils.warning( '删除资源 ' + url + '时出现了错误!' );
        };

        request.onloadend = function() {

            if (request.status != 200) {
                utils.warning( '删除资源 ' + url + '失败，服务器返回代码：' + request.status );
                return;
            }
            callback( JSON.parse( request.responseText ).token );
        };
        request.open('GET', url + '?' + params, true);
        request.send();
    }

    function upload_file(file, key, token) {
    }

    function upload_files() {
        var element = document.getElementById('resources-files');
        var files = element.files; /* now you can work with the file list */
        for (var i = 0, numFiles = files.length; i < numFiles; i++) {
            var file = files[i];
            var extra = {}, config = {};
            var observable = qiniu.upload(file, key, token, extra, config)
            var subscription = observable.subscribe(
                function next( res ) {
                    console.log( 'total bytes: ' + res.total.total + ', uploaded: ' + res.total.uploaded + ', Progress: ' + res.total.percent + '%' );
                },
                function error( err ) {
                    if ( err.isRequestError ) {
                        console.log( 'XHR Request error: ' + err.reqId );
                    }
                    else {
                        console.log( 'Server return error (' + err.code + '): ' + err.message );
                    }
                },
                function complete( res ) {
                    console.log( 'Uploaded complete.' );
                }
            );

            // 上传取消
            // subscription.unsubscribe()
        }
    }

    $(document).ready(function() {

        
        // active current section, maybe it's not required
        // $('#snsgis-titlebar-main-tabs').children().click(function(e) {
        //     $(this).siblings().removeClass('active');
        //     $(this).addClass('active');
        // });

        // ajax load, to fix history.back problem, refer to
        // https://github.com/browserstate/history.js
        // $('#snsgis-titlebar a.auto_ajax').click(function(e) {
        //     $('#content').load($(this).attr('href'), function(responseTxt,statusTxt,xhr) {
        //         if(statusTxt=='error')
        //             alert('Error: '+xhr.status+': '+xhr.statusText);
        //     });
        // });
      var cb = function(){
        if ($(this).hasClass('ajax-clickload-once'))
          $(this).off('click');
        var target = $(this).attr('data-target');
        var url = $(this).attr('href');
        var j = url.indexOf('?') === -1 ? '?' : '&';
        var head = $(this).attr('ajax-include-head');
        var para = head ? 'ajax_include_head=1' : 'ajax_load=1';
        url += j + para;
        $.get(url, function(data){
          if (head){
            var html = data;
            $(target).empty().append(html);
          }
          else{
            $(target).html(data);
            $(target + ' .ajax-clickload').attr('data-target', target).click(cb);
          }
        });

        // $(target).load(url, function(responseTxt,statusTxt,xhr){
        //   if(statusTxt=='error')
        //     console.log('Error: '+xhr.status+': '+xhr.statusText);
        //   else
        //     $(target + ' .ajax-clickload').attr('data-target', target).click(cb);
        // });
      };

      $('.ajax-clickload').click(function (e){
        e.preventDefault();
        cb.call(this);
      });
      $('.ajax-autoload').each(cb);
      // Activate tab
    });
});
