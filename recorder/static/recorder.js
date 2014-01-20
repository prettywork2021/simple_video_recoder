function embed_recorder() {
    params = {allowScriptAccess: "always"};
    attrs = {id: 'recorder'};
    flashvars = {fileName: rtmp_stream};
    swfobject.embedSWF(
        '/static/red5recorder.swf',
        'recorder',
        "300",
        "225",
        "8",
        null,
        flashvars,
        params,
        attrs
    );
}

var wait_timeout_id;
function wait_timeout() {
    $('.recording').hide();
    $('.wait').show();

    setTimeout(function(){
        $('.wait').hide();
        $('.recording').show();
    }, 30000);
}

$(document).ready(function(){
    $('.recording').click(function(){
        var rec_link = $(this);

        if (rec_link.hasClass('start')) {
            rec_link.hide();
            document.getElementById("recorder").startRecording();
            $.post('/start/' + rtmp_stream + '/', {'csrfmiddlewaretoken': csrf_token}, function(data){
                if (!data.success && data.cannot_record) {
                    wait_timeout();
                }
                else {
                    rec_link.addClass('stop').removeClass('start');
                    rec_link.html('Stop recording');
                    rec_link.show();
                }
            });

        }
        else if (rec_link.hasClass('stop')) {
            rec_link.hide();
            document.getElementById("recorder").stopRecording();
            $.post('/stop/' + rtmp_stream + '/', {'csrfmiddlewaretoken': csrf_token}, function(data){
                rtmp_stream = data.new_rtmp_stream;
                rec_link.addClass('start').removeClass('stop');
                rec_link.html('Start recording');
                wait_timeout();
                embed_recorder();
            });
        }

        return false;
    });

    $(document).on('click', '.video .delete', function(){
        var link = $(this);
        $.post(
            link.attr('href'),
            {'csrfmiddlewaretoken': csrf_token, 'video_dir': link.attr('data-dir')},
            function(){
                link.parents('.video').remove();
            }
        );

        return false;
    });

    embed_recorder();
});
