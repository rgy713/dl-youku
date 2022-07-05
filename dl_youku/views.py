# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.template import loader
import youtube_dl
import os
import mimetypes
import time
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from dj_youku import settings

def urlConvert(url):
    if "m.youku.com/video" in url:
        url = url.replace("m.youku.com/video", "v.youku.com/v_show")
    return url

def index(request):
    template = loader.get_template('dl_youku/index.html')
    context = {
        'title': "Youku Video Download",
    }
    return HttpResponse(template.render(context, request))


def getvideoinfo(request):
    if request.is_ajax():
        video_url = request.POST.get('url', None)

        if video_url == None:
            raise Http404('URL解析エラー')

        video_url = urlConvert(video_url)

        ydl = youtube_dl.YoutubeDL({'listformats': True})
        with ydl:
            result = ydl.extract_info(
                video_url,
                download=False  # We just want to extract the info
            )

        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            video = result
        print(video)
        data = {
            'result': "S_OK",
            "content": {
                'title': video['title'],
                'formats': video['formats_table']
            }
        }
        return JsonResponse(data)
    else:
        raise Http404('URL解析エラー')


def download(request):
    # BASE_DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if request.method == 'POST':

        video_url = request.POST.get('url', None)
        format_id = request.POST.get('formatid', None)
        is_ios = request.POST.get('isIos', None)

        if video_url == None:
            raise Http404('URL解析エラー')

        video_url = urlConvert(video_url)

        pre_name = 'Youku_'
        if 'tudou.com' in video_url:
            pre_name = 'Tudou_'

        params = {'outtmpl': settings.STORE_DIR_PATH + '/' + pre_name + '%(id)s.%(ext)s', 'embed-thumbnail': True
            , 'hls-prefer-ffmpeg': True, }

        if format_id != None:
            params['format'] = format_id

        ydl = youtube_dl.YoutubeDL(params)

        with ydl:
            result = ydl.extract_info(
                video_url,
                download=True  # We just want to extract the info
            )

        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            video = result

        dl_name = '%s%s.%s' % (pre_name, video['id'], video['ext'])
        # re_dl_name = '%s%s.%s' % ('YoukuVideo_', time.strftime("%Y%m%d%H%M%S"), video['ext'])

        filename = os.path.join(settings.STORE_DIR_PATH, dl_name)

        if is_ios == "false":
            chunk_size = 8192
            response = StreamingHttpResponse(FileWrapper(open(filename, 'rb'), chunk_size),
                                             content_type=mimetypes.guess_type(filename)[0])
            # response = FileResponse(open(filename, 'rb'))
            response['Content-Length'] = os.path.getsize(filename)
            response['Content-Disposition'] = "attachment; filename=%s" % dl_name
            response['Set-Cookie'] = 'fileDownload=true; path=/'
            return response
        else:
            videoUrl = '%s/%s' % (settings.STORE_HTTP_PATH, dl_name)
            data = {
                'result': "S_OK",
                "content": {
                    'videoUrl': videoUrl,
                }
            }
            return JsonResponse(data)

    else:
        raise Http404('URL解析エラー')
