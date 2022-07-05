from django.conf.urls import url

from . import views

app_name = 'dl_youku'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^download/$', views.download, name='download'),
    url(r'^getvideoinfo$', views.getvideoinfo, name='getvideoinfo'),
]