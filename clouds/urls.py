from django.conf.urls import patterns, include, url

urlpatterns = patterns('clouds.views',
    url(r'^$', 'home'), 
    url(r'^image/(?P<pk>\d+)$', 'image'), 
    url(r'^sidtime/(?P<pk>\d+)$', 'sidtime'), 
    url(r'^lines/$', 'lines'), 
    url(r'^lines/(?P<pk>\d+)/$', 'line'), 
    url(r'^lines/(?P<pk>\d+)/img/$', 'lineimg'), 
    url(r'^lines/(?P<line>\d+)/sidpoints/$', 'line_sidpoints'), 
    url(r'^lines/(?P<line>\d+)/sidpoints/plot/$', 'line_sidpoints_plot'), 
    url(r'^lines/(?P<line>\d+)/sidpoints/plot/(?P<hour>\d+)/$', 'line_sidpoints_plot_hour'), 
    url(r'^lines/(?P<line>\d+)/realpoints/$', 'line_realpoints'), 
    url(r'^lines/(?P<line>\d+)/realpoints/plot/$', 'line_realpoints_plot'), 
    url(r'^lines/(?P<line>\d+)/realpoints/plot/(?P<year>\d+)/$', 'line_realpoints_plot'), 
    url(r'^lines/(?P<line>\d+)/realpoints/plot/(?P<year>\d+)/(?P<month>\d+)/$', 'line_realpoints_plot'), 
    url(r'^lines/(?P<line>\d+)/realpoints/plot/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'line_realpoints_plot_day'), 
    url(r'^lines/(?P<line>\d+)/realpoints/sidplot/$', 'line_realpoints_sidplot'), 
    url(r'^plot/$', 'plot'), 
    url(r'^plot/(?P<year>\d+)/$', 'plot'), 
    url(r'^plot/(?P<year>\d+)/(?P<month>\d+)/$', 'plot'), 
    url(r'^plot/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'plot_day'), 
    url(r'^ani/(\d+)/(\d+)/(\d+)/$', 'ani'), 
    url(r'^random/$', 'random_view'), 
    url(r'^random.tex$', 'random_view_tex'), 
)

from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
