# coding: utf-8
import time
import json
import os
import shutil
import random
import requests
import subprocess
import xml.etree.ElementTree as ET
import urllib2

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.http import require_http_methods
from multiprocessing import Process


def mp4_convert(request, rtmp_stream, flv_path, mp4_path):
    subprocess.call([
        'ffmpeg',
        '-i', flv_path,
        '-vcodec', 'libx264',
        '-profile:v', 'baseline',
        '-preset', 'slow',
        '-b:v', '180k',
        '-maxrate', '500k',
        '-bufsize', '1000k',
        '-vf', 'scale=-1:240',
        '-threads', '0',
        '-acodec', 'libvo_aacenc',
        '-b:a', '128k',
        '-y',
        mp4_path
    ])

    request.session['convert'][rtmp_stream]['mp4'] = True


def webm_convert(request, rtmp_stream, flv_path, webm_path):
    subprocess.call([
        'ffmpeg',
        '-i', flv_path,
        '-vcodec', 'libvpx',
        '-acodec', 'libvorbis',
        '-ac', '2',
        '-ab', '128k',
        '-ar', '44100',
        '-b', '180k',
        '-vf', 'scale=-1:240',
        '-threads', '0',
        '-y',
        webm_path
    ])

    request.session['convert'][rtmp_stream]['webm'] = True


def generate_stream_name():
    return "".join([str(int(time.time())), str(random.randint(1, 1000))])


def can_record(request):
    can_record = True
    if 'last_record_time' in request.session and (time.time() - request.session['last_record_time']) < 30:
        can_record = False

    return can_record


def home(request):
    rtmp_stream =  generate_stream_name()

    converting = []
    converting_names = []
    if 'convert' in request.session:
        for (stream_name, stream) in request.session['convert'].items():
            remaining = stream['estimate'] - (time.time() - stream['start'])
            if remaining > 0:
                converting.append(int(remaining))
                converting_names.append(stream_name)

    records = []
    records_dir = os.path.join(settings.PROJECT_ROOT, 'media', 'records')
    if os.path.exists(records_dir):
        for record in os.listdir(records_dir):
            if not record in converting_names:
                record_dir = os.path.join('/', 'media', 'records', record)
                records.append({
                    'dir': record,
                    'mp4': os.path.join(record_dir, 'video.mp4'),
                    'webm': os.path.join(record_dir, 'video.webm'),
                })

    return render_to_response(
        'home.html',
        {
            'rtmp_stream': rtmp_stream,
            'records': records,
            'can_record': can_record(request),
            'converting': converting
        },
        RequestContext(request)
    )


def live(request):
    url = settings.RTMP_CONTROL_HOST + '/stat/'
    ip_request = urllib2.Request(url)
    root = ET.parse(urllib2.urlopen(ip_request)).getroot()

    streams = []
    for stream in root.findall('./server/application/live/stream'):
        streams.append(stream.findall('./name')[0].text)

    return render_to_response(
        'live.html',
        {'streams': streams, 'server': settings.RTMP_SERVER},
        RequestContext(request)
    )


def live_hls(request):
    url = settings.RTMP_CONTROL_HOST + '/stat/'
    ip_request = urllib2.Request(url)
    root = ET.parse(urllib2.urlopen(ip_request)).getroot()

    streams = []
    for stream in root.findall('./server/application/live/stream'):
        streams.append(stream.findall('./name')[0].text)

    return render_to_response(
        'live.html',
        {'streams': streams, 'server': settings.HLS_RTMP_SERVER, 'hls': True},
        RequestContext(request)
    )


def start(request, rtmp_stream):
    if not can_record(request):
        data = json.dumps({'success': False, 'cannot_record': True})

    params = {'app': 'my_videos', 'name': rtmp_stream, 'rec': 'my_recorder'}

    # текст ответа на запрос к nginx rtmp control будет путь к записываемому файлу
    response = requests.get(settings.RTMP_CONTROL_HOST + '/control/record/start', params=params)

    request.session[rtmp_stream] = response.text
    data = json.dumps({'success': True, 'rtmp_stream': rtmp_stream})

    return HttpResponse(data, content_type='application/json')


def stop(request, rtmp_stream):
    request.session['last_record_time'] = time.time()
    temp_flv_path = request.session[rtmp_stream]

    records_path = os.path.join(settings.MEDIA_ROOT, 'records', rtmp_stream)
    if not os.path.exists(records_path):
        os.makedirs(records_path)

    flv_path = os.path.join(records_path, 'video.flv')

    # добавляем метаданные в видео-файл
    subprocess.call(['yamdi', '-i', temp_flv_path, '-o', flv_path])

    mp4_path = os.path.join(records_path, 'video.mp4')
    webm_path = os.path.join(records_path, 'video.webm')

    if not 'convert' in request.session:
        request.session['convert'] = {}

    request.session['convert'][rtmp_stream] = {
        'start': time.time(),
        'estimate': int(os.stat(temp_flv_path).st_size * 0.000003650)
    }

    Process(target=mp4_convert, args=(request, rtmp_stream, flv_path, mp4_path)).start()
    Process(target=webm_convert, args=(request, rtmp_stream, flv_path, webm_path)).start()

    next_stream_name = generate_stream_name()

    return HttpResponse(json.dumps({'status': 'OK', 'new_rtmp_stream': next_stream_name}), content_type='application/json')


@require_http_methods(['POST'])
def delete_video(request):
    video_dir = request.POST.get('video_dir')
    video_dir_path = os.path.join(settings.PROJECT_ROOT, 'media', 'records', video_dir)
    if os.path.exists(video_dir_path):
        shutil.rmtree(video_dir_path)

    return HttpResponse(json.dumps({'status': 'OK'}), content_type='application/json')
