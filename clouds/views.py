from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from clouds.models import Line, SidPoint, RealPoint, Image, SidTime
from django.db.models import Count
from django.utils.http import urlquote_plus
import subprocess, tempfile, re, os, datetime
import settings
from django.core.urlresolvers import reverse
import datetime
import hashlib
from django.db.models import Q

class LineListView(ListView):
    paginate_by=100
    order_fields = ['id', 'ratio', 'max_flux', 'stddev_flux', 'sidpoint_count', 'realpoint_count']

    def get_queryset(self):
        queryset = Line.objects.order_by('pk')
        if 'ratio' in self.request.GET:
            queryset = Line.objects.filter(max_flux__gt=0, stddev_flux__gt=0).extra(select={'ratio':'stddev_flux/max_flux'})

        if 'filter' in self.request.GET:
            try:
                minpoints = int(self.request.GET['minpoints'])
            except KeyError:
                minpoints = 20
            if self.request.GET['filter'] == 'sid':
                queryset = queryset.filter(sidpoint_count__gt=minpoints) 
            elif self.request.GET['filter'] == 'real':
                queryset = queryset.filter(realpoint_count__gt=minpoints) 

        if 'order' in self.request.GET:
            field = self.request.GET['order']

            if field in self.order_fields + map(lambda x:'-'+x, self.order_fields):
                queryset = queryset.order_by(field)

        return queryset

    def get_context_data(self, **context):
        query = self.request.GET.copy()
        if 'page' in query:
            del query['page']
        return super(LineListView, self).get_context_data(
            order_fields=self.order_fields,
            querystring=query.urlencode(),
            **context)

class PointsView(ListView):
    template_name = 'clouds/point_list.html'
    closest = None

    def get_queryset(self):
        queryset = self.model.objects

        if self.model == RealPoint:
            queryset = queryset.prefetch_related('image')
        elif self.model == SidPoint:
            queryset = queryset.prefetch_related('sidtime')
            if 'ends' in self.request.GET:
                queryset = queryset.filter( Q(prev=None) | Q(sidpoint=None) )

        if 'line' in self.kwargs:
            queryset = queryset.filter(line__pk=self.kwargs['line'])

        return queryset

    def get_context_data(self, **context):
        context.update(closest=self.closest)
        return super(PointsView, self).get_context_data(**context)

class PaginatedPointsView(PointsView):
    paginate_by=1000

    def get_queryset(self):
        queryset = super(PaginatedPointsView, self).get_queryset()
        if 'timestamp' in self.request.GET:
            # TODO Modify the pagination message to be clear that this isn't necessarily everything
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            #queryset1 = queryset.filter(image__datetime__lt=dt).order_by('-image__datetime')[0:(self.paginate_by/2)]
            #queryset2 = queryset.filter(image__datetime__gt=dt).order_by('image__datetime')[0:(self.paginate_by/2)]
            if self.model == SidPoint:
                t = dt.time()
                queryset1 = queryset.filter(sidtime__time__lte=t).order_by('-sidtime__time')[0:20]
                queryset2 = queryset.filter(sidtime__time__gt=t).order_by('sidtime__time')[0:20]
            else:
                queryset1 = queryset.filter(image__datetime__lte=dt).order_by('-image__datetime')[0:20]
                queryset2 = queryset.filter(image__datetime__gt=dt).order_by('image__datetime')[0:20]
            self.closest = queryset1[0]
            return list(reversed(queryset1)) + list(queryset2)
        return queryset

class DatePointsView(PointsView):
    def get_queryset(self):
        queryset = super(DatePointsView, self).get_queryset()
        kwargs = self.kwargs
        dt_from = datetime.datetime(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        dt_to = dt_from + datetime.timedelta(days=1)
        return queryset.filter(image__datetime__gt=dt_from, image__datetime__lt=dt_to).order_by('image__datetime')

class HourPointsView(PointsView):
    def get_queryset(self):
        queryset = super(HourPointsView, self).get_queryset()
        hour = int(self.kwargs['hour'])
        return queryset.filter(
            sidtime__time__gte=datetime.time(hour, 0),
            sidtime__time__lte=datetime.time(hour, 59, 59)
        ).order_by('sidtime__time')

class PlotView(object):
    gnuplot_date_format = '%Y-%m-%d'
    gnuplot_column_no = 3
    gnuplot_size = '1600,900'
    gnuplot_lines = False
    gnuplot_timefmt = '%Y-%m-%d %H:%M:%S'
    extra_commands = ''
    context = {}

    template_name = 'clouds/plot.html'

    def get_context_data(self, **context):
        self.gnuplot_lines = 'lines' in self.request.GET
        if 'w' in self.request.GET and 'h' in self.request.GET:
            self.gnuplot_size = '{0},{1}'.format(
                int(self.request.GET['w']),
                int(self.request.GET['h'])
            )
        if 'ymax' in self.request.GET:
            self.extra_commands += "\nset yrange [0:{0}]".format(float(self.request.GET['ymax']))

        data_file = self.get_data_file()
        command_string = """
set timefmt "{6}"
set xdata time
set terminal png size {0} 
set format x '{1}'
{2}
plot '{3}' using 1:{4} {5}
show variables all
""".format(
           self.gnuplot_size,
           self.gnuplot_date_format,
           self.extra_commands,
           data_file.name,
           self.gnuplot_column_no,
           ('w lines' if self.gnuplot_lines else ''),
           self.gnuplot_timefmt
        )
        image = hashlib.md5(command_string).hexdigest()+urlquote_plus(
                    self.request.META['PATH_INFO'].replace('/','-'))+'.png'
        output_filename = os.path.join(settings.MEDIA_ROOT, 'tmp', image)
        imagesrc = 'tmp/'+image
        command_file = tempfile.NamedTemporaryFile()
        stdout_file = tempfile.NamedTemporaryFile()
        command_file.write(
            "set output '{0}'\n".format(output_filename)+command_string)
        command_file.flush()
        exitcode = subprocess.call(['gnuplot', command_file.name], stdout=stdout_file, stderr=stdout_file)
        stdout_file.flush()
        stdout_file.seek(0)
        if exitcode != 0:
            raise Exception('gnuplot exited unsuccessfully, here is its output:\n'+stdout_file.read())
        gpval_regex = re.compile('\tGPVAL_([A-Z_]*) = "?(.*)"?')
        gpval = {}
        for line in stdout_file.readlines():
            m = gpval_regex.match(line)
            if m:
                gpval[m.group(1)] = m.group(2)
        # X_MIN X_MAX TERM_XMIN TERM_XMAX etc.
        data_file.close()

        context.update({'imagesrc': imagesrc,
                        'gpval': gpval,
                        'mouseover': 'm' in self.request.GET,
                      })
        context.update(self.context)
        return context

class DatePlotView(PlotView):
    template_prefix = 'clouds.views.plot'

    def get(self, request, year=None, month=None, day=None, **kwargs):
        if 'timestamp' in request.GET and not day:
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            suffix = ''
            if day:
                return HttpResponse('test')
            elif month or 'day' in request.GET:
                kwargs.update(year=dt.year,month=dt.month,day=dt.day)
                suffix = '_day'
            elif year:
                kwargs.update(year=dt.year,month=dt.month)
            else:
                kwargs.update(year=dt.year)
            q = request.GET.copy()
            if 'day' in request.GET:
                del q['day']
            else:
                del q['timestamp']
            return HttpResponseRedirect(reverse(self.template_prefix+suffix, kwargs=kwargs)+'?'+q.urlencode())
        self.context['querystring'] = request.GET.urlencode()

        if year:
            dt_from = datetime.datetime(int(year), int(month or 1), int(day or 1))
            if day:
                dt_to = dt_from + datetime.timedelta(days=1)
                self.gnuplot_date_format = '%H:%M'
            elif month:
                if month == '12':
                    dt_to = datetime.datetime(int(year)+1, 1, 1)
                else:
                    dt_to = datetime.datetime(int(year), int(month)+1, 1)
            else:
                dt_to = datetime.datetime(int(year)+1, 1, 1)

            self.extra_commands = """set xrange ['{0}':'{1}']""".format(
                    dt_from, dt_to)
        return super(DatePlotView, self).get(request)

class PointsPlotView(PlotView, PointsView):
    def get_data_file(self):
        data_file = tempfile.NamedTemporaryFile()
        active_only = not 'all' in self.request.GET 
        inactive_only = 'inactive' in self.request.GET
        for point in self.object_list:
            if (self.model != RealPoint
             or (not active_only and not inactive_only)
             or (active_only and point.active)
             or (inactive_only and not point.active)):
                if self.model == RealPoint:
                    data_file.write(unicode(point.image.datetime))
                else:
                    data_file.write(unicode(point.sidtime.time))
                data_file.write(' ')
                data_file.write(unicode(point.flux))
                data_file.write('\n')
                data_file.flush()
        return data_file

    def get_context_data(self, **context):
        if 'timestamp' in self.request.GET:
            context.update(timestamp=int(self.request.GET['timestamp'].split('.')[0]))
        context.update(line=self.kwargs['line'])
        return super(PointsPlotView, self).get_context_data(**context)

class RealPointsPlotView(DatePlotView, PointsPlotView):
    template_prefix = 'clouds.views.line_realpoints_plot'
    pass

class SidPointsPlotView(PointsPlotView):
    gnuplot_timefmt='%H:%M:%S'
    gnuplot_date_format='%H:%M'
    gnuplot_column_no=2

    def get(self, request, hour=None, **kwargs):
        if 'timestamp' in request.GET:
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            kwargs.update(hour=dt.time().hour)
            q = request.GET.copy()
            del q['timestamp']
            return HttpResponseRedirect(reverse('clouds.views.line_sidpoints_plot_hour', kwargs=kwargs)+'?'+q.urlencode())
        if hour:
            self.extra_commands = """set xrange ['{0}:00':'{1}:00']""".format(int(hour), int(hour)+1)
        return super(SidPointsPlotView, self).get(request, **kwargs)

class CloudsPlotView(DatePlotView, TemplateView):
    
    def get(self, request, *args, **kwargs):
        if 'column' in request.GET:
            self.gnuplot_column_no = int(request.GET['column'])

        return super(CloudsPlotView, self).get(request, *args, **kwargs)

    def get_data_file(self):
        if 'minpoints' in self.request.GET:
            minpoints = int(self.request.GET['minpoints'])
        else: minpoints = 1
        datafilename = 'sum'+str(minpoints)+'data' + ('_infsig' if 'infsig' in self.request.GET else '')
        return open(os.path.join('out', datafilename), 'r')

class AniView(ListView):
    template_name = 'clouds/ani.html'
    def get_queryset(self):
        kwargs = self.kwargs
        dt_from = datetime.datetime(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        dt_to = dt_from + datetime.timedelta(days=1)
        return Image.objects.filter(datetime__gt=dt_from, datetime__lt=dt_to).order_by('datetime')


class DoubleViewMixin(object):
    gnuplot_size = '900,900'

    def __init__(self, **kwargs):
        out = super(DoubleViewMixin, self).__init__(**kwargs)
        class OutputlessSeconary(self.secondary_class):
            def get(self, request, *args, **kwargs):
                return self.get_context_data(
                        object_list=self.get_queryset(), **kwargs)
        self.secondary = OutputlessSeconary.as_view(**kwargs)
        return out
    
    def dispatch(self, request, *args, **kwargs):
        self.secondary_context_data = self.secondary(request, *args, **kwargs)
        return super(DoubleViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **context):
        context.update(self.secondary_context_data)
        return super(DoubleViewMixin, self).get_context_data(**context)

class AniCloudsPlotView(DoubleViewMixin, CloudsPlotView):
    secondary_class = AniView
    template_name = 'clouds/ani_plot.html'

class AniRealPointsPlotView(DoubleViewMixin, RealPointsPlotView):
    secondary_class = DatePointsView
    template_name = 'clouds/ani_plot_line_realpoints.html'

    def get_context_data(self, **context):
        if 'zoom' in self.request.GET:
            self.extra_commands = """set xrange ['{0}':'{1}']""".format(
                    self.secondary_context_data['object_list'][0].image.datetime,
                    self.secondary_context_data['object_list'][-1].image.datetime)
            self.gnuplot_date_format = '%H:%M'
        return super(AniRealPointsPlotView, self).get_context_data(**context)

class AniSidPointsPlotView(DoubleViewMixin, SidPointsPlotView):
    secondary_class = HourPointsView
    template_name = 'clouds/ani_plot_line_realpoints.html'

class TimeNavDetailView(DetailView):
    date_field = 'datetime'
    
    def get_next(self, filter_field, order):
        q = self.model.objects.filter(**{filter_field: getattr(self.object, self.date_field)}).order_by(order) 
        try:
            return q[0]
        except IndexError:
            return self.model.objects.order_by(order)[0]

    def get_context_data(self, **context):
        context.update(
            prev = self.get_next(self.date_field+'__lt', '-'+self.date_field),
            next = self.get_next(self.date_field+'__gt', self.date_field),
        )
        return super(TimeNavDetailView, self).get_context_data(**context)

class ImageView(TimeNavDetailView):
    def get_context_data(self, **context):
        context.update(point_pk=int(self.request.GET.get('point', 0)))
        return super(ImageView, self).get_context_data(**context)

home = TemplateView.as_view(template_name='clouds/home.html')

lines = LineListView.as_view()
line = DetailView.as_view(model=Line)

line_sidpoints = PaginatedPointsView.as_view(model=SidPoint)
line_sidpoints_plot = SidPointsPlotView.as_view(model=SidPoint)
line_sidpoints_plot_hour = AniSidPointsPlotView.as_view(model=SidPoint)

line_realpoints = PaginatedPointsView.as_view(model=RealPoint)
line_realpoints_plot = RealPointsPlotView.as_view(model=RealPoint)
line_realpoints_plot_day = AniRealPointsPlotView.as_view(model=RealPoint)

plot = CloudsPlotView.as_view()
ani = AniView.as_view()
plot_day = AniCloudsPlotView.as_view()

image = ImageView.as_view(model=Image)
sidtime = ImageView.as_view(model=SidTime, date_field='time')

