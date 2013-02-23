from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from clouds.models import Line, SidPoint, RealPoint, Image
from django.db.models import Count
from django.utils.http import urlquote_plus
import subprocess, tempfile, re, os, datetime
import settings
from django.core.urlresolvers import reverse
import datetime
import hashlib

def home(request):
    return HttpResponse('This page intentionally left blank.')

class LineListView(ListView):
    paginate_by=100

    def get_queryset(self):
        queryset = Line.objects.order_by('pk')
        if 'filter' in self.request.GET:
            if self.request.GET['filter'] == 'sid':
                queryset = queryset.annotate(Count('sidpoint')).filter(sidpoint__count__gt=20) 
            elif self.request.GET['filter'] == 'real':
                queryset = queryset.annotate(Count('realpoint')).filter(realpoint__count__gt=20) 
        return queryset

class PointsView(ListView):
    template_name = 'clouds/point_list.html'
    closest = None

    def get_queryset(self):
        queryset = self.model.objects

        if self.model == RealPoint:
            queryset = queryset.prefetch_related('image')
        elif self.model == SidPoint:
            queryset = queryset.prefetch_related('sidtime')

        if 'line' in self.kwargs:
            queryset = queryset.filter(line__pk=self.kwargs['line'])


        return queryset

    def get_context_data(self, **context):
        return super(PointsView, self).get_context_data(closest=self.closest, **context)

class PaginatedPointsView(PointsView):
    paginate_by=1000

    def get_queryset(self):
        queryset = super(PaginatedPointsView, self).get_queryset()
        if 'timestamp' in self.request.GET:
            # TODO Modify the pagination message to be clear that this isn't necessarily everything
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            #queryset1 = queryset.filter(image__datetime__lt=dt).order_by('-image__datetime')[0:(self.paginate_by/2)]
            #queryset2 = queryset.filter(image__datetime__gt=dt).order_by('image__datetime')[0:(self.paginate_by/2)]
            queryset1 = queryset.filter(image__datetime__lte=dt).order_by('-image__datetime')[0:20]
            queryset2 = queryset.filter(image__datetime__gt=dt).order_by('image__datetime')[0:20]
            self.closest = queryset1[0]
            return list(reversed(queryset1)) + list(queryset2)
        else:
            queryset = queryset.order_by('pk')
        return queryset

class PlotView(object):
    gnuplot_date_format = '%Y-%m-%d'
    gnuplot_column_no = 3
    gnuplot_size = '1600,900'
    gnuplot_lines = False
    extra_commands = ''
    context = {}

    def get_context_data(self, **context):
        self.gnuplot_lines = 'lines' in self.request.GET
        if 'w' in self.request.GET and 'h' in self.request.GET:
            self.gnuplot_size = '{0},{1}'.format(
                int(self.request.GET['w']),
                int(self.request.GET['h'])
            )

        data_file = self.get_data_file()
        command_string = """
set timefmt "%Y-%m-%d %H:%M:%S"
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
           ('w lines' if self.gnuplot_lines else '')
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

class PointsPlotView(PlotView, PointsView):
    template_name = 'clouds/plot_line_realpoints.html'

    def get_data_file(self):
        data_file = tempfile.NamedTemporaryFile()
        for point in self.object_list:
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
            context.update(timestamp=int(self.request.GET['timestamp']))
        context.update(line=self.kwargs['line'])
        return super(PointsPlotView, self).get_context_data(**context)

class CloudsPlotView(PlotView, TemplateView):
    template_name = 'clouds/plot.html'
    line_minimum_points = 1
    
    def get(self, request, year=None, month=None, day=None):
        if 'timestamp' in request.GET:
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            suffix = ''
            if day:
                return HttpResponse('test')
            elif month:
                args=(dt.year,dt.month,dt.day,)
                suffix = '_day'
            elif year:
                args=(dt.year,dt.month,)
            else:
                args=(dt.year,)
            q = request.GET.copy()
            del q['timestamp']
            return HttpResponseRedirect(reverse('clouds.views.plot'+suffix, args=args)+'?'+q.urlencode())
        self.context['querystring'] = request.GET.urlencode()

        if 'column' in request.GET:
            self.gnuplot_column_no = int(request.GET['column'])
        if 'minpoints' in request.GET:
            self.line_minimum_points = int(request.GET['minpoints'])
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
        return super(CloudsPlotView, self).get(request)

    def get_data_file(self):
        return open(os.path.join('out', 'sum'+str(self.line_minimum_points)+'data'), 'r')

class AniView(ListView):
    template_name = 'clouds/ani.html'
    def get_queryset(self):

        dt_args = map(int, self.args)
        dt_from = datetime.datetime(*dt_args)
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

class AniPointsPlotView(DoubleViewMixin, PointsPlotView):
    secondary_class = PaginatedPointsView
    template_name = 'clouds/ani_plot_line_realpoints.html'


lines = LineListView.as_view()
line = DetailView.as_view(model=Line)

line_sidpoints = PaginatedPointsView.as_view(model=SidPoint)
line_realpoints = PaginatedPointsView.as_view(model=RealPoint)
line_realpoints_plot = PointsPlotView.as_view(model=RealPoint)
line_realpoints_ani_plot = AniPointsPlotView.as_view(model=RealPoint)

plot = CloudsPlotView.as_view()
ani = AniView.as_view()
plot_day = AniCloudsPlotView.as_view()

image = DetailView.as_view(model=Image)
