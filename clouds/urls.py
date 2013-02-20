from django.conf.urls import patterns, include, url

urlpatterns = patterns('clouds.views',
    url(r'^$', 'home'), 
    url(r'^lines/$', 'lines'), 
    url(r'^lines/(?P<pk>\d+)/$', 'line'), 
    url(r'^lines/(?P<line>\d+)/sidpoints/$', 'line_sidpoints'), 
    url(r'^lines/(?P<line>\d+)/realpoints/$', 'line_realpoints'), 
    url(r'^lines/(?P<line>\d+)/realpoints/plot/$', 'line_realpoints_plot'), 
    url(r'^lines/(?P<line>\d+)/realpoints/aniplot/$', 'line_realpoints_ani_plot'), 
    url(r'^plot/$', 'plot'), 
    url(r'^plot/(\d+)/$', 'plot'), 
    url(r'^plot/(\d+)/(\d+)/$', 'plot'), 
    url(r'^plot/(\d+)/(\d+)/(\d+)/$', 'plot_day'), 
    url(r'^ani/(\d+)/(\d+)/(\d+)/$', 'ani'), 
)

from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
