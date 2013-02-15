from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from clouds.models import Line, SidPoint, RealPoint
from django.db.models import Count
from django.utils.http import urlquote_plus
import subprocess, tempfile, re, os, datetime
import settings


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

class PointsPlotView(PointsView):
    template_name = 'clouds/plot.html'

    def get_context_data(self, object_list):
        image = urlquote_plus(self.request.META['PATH_INFO'].replace('/','-'))+'.png'
        output_filename = os.path.join(settings.MEDIA_ROOT, 'tmp', image)
        imagesrc = 'tmp/'+image
        data_file = tempfile.NamedTemporaryFile()
        for point in object_list:
            if self.model == RealPoint:
                data_file.write(unicode(point.image.datetime))
            else:
                data_file.write(unicode(point.sidtime.time))
            data_file.write(' ')
            data_file.write(unicode(point.flux))
            data_file.write('\n')
        command_file = tempfile.NamedTemporaryFile()
        stdout_file = tempfile.NamedTemporaryFile()
        command_file.write("""
set timefmt "%Y-%m-%d %H:%M:%S"
set xdata time
set terminal png size 1600,900
set output '{0}'
set format x "%Y-%m-%d"
plot'{1}' using 1:3
show variables all
""".format(output_filename, data_file.name))
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
        return {'imagesrc': imagesrc, 'gpval': gpval, 'line':self.kwargs['line']}

lines = LineListView.as_view()
line = DetailView.as_view(model=Line)

line_sidpoints = PointsView.as_view(model=SidPoint)
line_realpoints = PointsView.as_view(model=RealPoint)
line_realpoints_plot = PointsPlotView.as_view(model=RealPoint)
