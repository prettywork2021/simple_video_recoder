$(document).ready(function(){

    for (var i = 0; i < streams.length; i++) {
        $('body').append($('<div>').attr('id', 'stream' + i).attr('class', 'stream'));
        
        $f("stream" + i, '/static/flowplayer/flowplayer-3.2.18.swf', {
            clip: {
                url: streams[i],
                live: true,
                paused: true,
                provider: 'influxis'
            },
         
            plugins: {
                influxis: {
                    url: "/static/flowplayer/flowplayer.rtmp-3.2.13.swf",
                    netConnectionUrl: server
                }
            }
        });
    }

});
