from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from clouds.models import Line, SidPoint, RealPoint
from django.db.models import Count
from django.utils.http import urlquote_plus
import subprocess, tempfile, re, os, datetime
import settings
from django.core.urlresolvers import reverse
import datetime

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
    paginate_by=1000
    closest = None

    def get_queryset(self):
        queryset = self.model.objects

        if self.model == RealPoint:
            queryset = queryset.prefetch_related('image')
        elif self.model == SidPoint:
            queryset = queryset.prefetch_related('sidtime')

        if 'line' in self.kwargs:
            queryset = queryset.filter(line__pk=self.kwargs['line'])

        if 'timestamp' in self.request.GET:
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            #queryset1 = queryset.filter(image__datetime__lt=dt).order_by('-image__datetime')[0:(self.paginate_by/2)]
            #queryset2 = queryset.filter(image__datetime__gt=dt).order_by('image__datetime')[0:(self.paginate_by/2)]
            queryset1 = queryset.filter(image__datetime__lt=dt).order_by('-image__datetime')[0:20]
            queryset2 = queryset.filter(image__datetime__gt=dt).order_by('image__datetime')[0:20]
            self.closest = queryset1[0]
            return list(reversed(queryset1)) + list(queryset2)
        else:
            queryset = queryset.order_by('pk')

        return queryset

    def get_context_data(self, **context):
        return super(PointsView, self).get_context_data(closest=self.closest, **context)

class PlotView(object):
    gnuplot_date_format = '%Y-%m-%d'
    gnuplot_column_no = 3
    extra_commands = ''
    context = {}

    def get_context_data(self, **context):
        image = urlquote_plus(self.request.META['PATH_INFO'].replace('/','-'))+'.png'
        output_filename = os.path.join(settings.MEDIA_ROOT, 'tmp', image)
        imagesrc = 'tmp/'+image
        data_file = self.get_data_file()
        command_file = tempfile.NamedTemporaryFile()
        stdout_file = tempfile.NamedTemporaryFile()
        command_file.write("""
set timefmt "%Y-%m-%d %H:%M:%S"
set xdata time
set terminal png size 1600,900
set output '{0}'
set format x '{1}'
{2}
plot '{3}' using 1:{4}
show variables all
""".format(output_filename,
           self.gnuplot_date_format,
           self.extra_commands,
           data_file.name,
           self.gnuplot_column_no))
        command_file.flush()
        data_file.flush()
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
        print output_filename
        context.update({'imagesrc': imagesrc, 'gpval': gpval})
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
        return data_file

    def get_context_data(self, **context):
        return super(PointsPlotView, self).get_context_data(
                line=self.kwargs['line'],
                **context)

class CloudsPlotView(PlotView, TemplateView):
    template_name = 'clouds/plot.html'
    
    def get(self, request, year=None, month=None, day=None):
        if 'timestamp' in self.request.GET:
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            if year:
                if month:
                    args=(dt.year,dt.month,dt.day,)
                else:
                    args=(dt.year,dt.month,)
            else:
                args=(dt.year,)
            return HttpResponseRedirect(reverse('clouds.views.plot', args=args))
        if 'column' in self.request.GET:
            self.gnuplot_column_no = int(self.request.GET['column'])
            self.context['column'] = self.gnuplot_column_no
        if year:
            dt_from = datetime.datetime(int(year), int(month or 1), int(day or 1))
            if day:
                dt_to = dt_from + datetime.timedelta(days=1)
                self.gnuplot_date_format = '%H:%M'
            elif month:
                if month == 12:
                    dt_to = datetime.datetime(int(year)+1, 1, 1)
                else:
                    dt_to = datetime.datetime(int(year), int(month)+1, 1)
            else:
                dt_to = datetime.datetime(int(year)+1, 1, 1)
            self.extra_commands = """set xrange ['{0}':'{1}']""".format(
                    dt_from, dt_to)
        return super(CloudsPlotView, self).get(request)

    def get_data_file(self):
        return open(os.path.join('out', 'sum2data'), 'r')

lines = LineListView.as_view()
line = DetailView.as_view(model=Line)

line_sidpoints = PointsView.as_view(model=SidPoint)
line_realpoints = PointsView.as_view(model=RealPoint)
line_realpoints_plot = PointsPlotView.as_view(model=RealPoint)
plot = CloudsPlotView.as_view()

