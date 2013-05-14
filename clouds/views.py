from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView
from clouds.models import Line, SidPoint, RealPoint, Image, SidTime
from django.db.models import Count
from django.utils.http import urlquote_plus
import subprocess, tempfile, re, os, datetime
import settings
from django.core.urlresolvers import reverse
import datetime, random
from django.db.models import Q
import hashlib
import PIL.Image, PIL.ImageDraw
import StringIO

class LineListView(ListView):
    paginate_by=100
    #order_fields = ['id', 'ratio', 'max_flux', 'stddev_flux', 'sidpoint_count', 'realpoint_count']
    order_fields = ['id', 'max_flux', 'stddev_flux', 'sidpoint_count', 'realpoint_count']

    def get_queryset(self):
        queryset = Line.objects.prefetch_related('linevalues_set')
        linevaluegeneration = int(self.request.GET.get('lvg', 2))
        queryset = queryset.extra(select = {'linevaluegeneration': linevaluegeneration})
        queryset = queryset.filter(linevalues__generation__pk=linevaluegeneration)

        if 'ratio' in self.request.GET:
            queryset = Line.objects.filter(max_flux__gt=0, stddev_flux__gt=0).extra(select={'ratio':'stddev_flux/max_flux'})

        if 'filter' in self.request.GET:
            try:
                minpoints = int(self.request.GET['minpoints'])
            except KeyError:
                minpoints = 200
            if self.request.GET['filter'] == 'sid':
                queryset = queryset.filter(sidpoint_count__gt=minpoints) 
            elif self.request.GET['filter'] == 'real':
                queryset = queryset.filter(realpoint_count__gt=minpoints) 

        if 'order' in self.request.GET:
            field = self.request.GET['order']

            if field in self.order_fields + map(lambda x:'-'+x, self.order_fields):
                if field != 'id':
                    field = ('-' if field.startswith('-') else '')+'linevalues__'+field.lstrip('-')
                queryset = queryset.order_by(field)
        else:
            queryset.order_by('pk')

        return queryset

    def get_context_data(self, **context):
        query = self.request.GET.copy()
        if 'page' in query:
            del query['page']
        return super(LineListView, self).get_context_data(
            order_fields=self.order_fields,
            order=self.request.GET.get('order', ''),
            querystring=query.urlencode(),
            ends='ends' in self.request.GET,
            **context)

class LineImage():
    pass

class PointsView(ListView):
    template_name = 'clouds/point_list.html'
    closest = None

    def get_queryset(self):
        queryset = self.model.objects

        if self.model == RealPoint:
            queryset = queryset.select_related('image')
            queryset = queryset.filter(generation=int(self.request.GET.get('g',1)))
            if 'nomoon' in self.request.GET:
                queryset = queryset.filter(image__moon=False)
            if 'moon' in self.request.GET:
                queryset = queryset.filter(image__moon=True)
        elif self.model == SidPoint:
            queryset = queryset.select_related('sidtime')
            if 'ends' in self.request.GET:
                queryset = queryset.filter( Q(prev=None) | Q(sidpoint=None) )

        if 'line' in self.kwargs:
            queryset = queryset.filter(line__pk=self.kwargs['line'])
            line = Line.objects.get(pk=self.kwargs['line'])

        return queryset

    def get_context_data(self, **context):
        context.update(closest=self.closest,
            line=self.kwargs.get('line'))
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
    gnuplot_column_no = 4
    gnuplot_size = '1400,700'
    gnuplot_lines = False
    gnuplot_timefmt = '%Y-%m-%d %H:%M:%S'
    extra_commands = ''
    context = {}

    template_name = 'clouds/plot_wrapped.html'

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
set timefmt "{7}"
set xdata time
set xlabel "Date/Time"
set ylabel "{8}"
unset key
set terminal png size {0} 
set format x '{1}'
{2}
plot '{3}' using 1:{4} {5} {6}
show variables all
""".format(
           self.gnuplot_size,
           self.gnuplot_date_format,
           self.extra_commands,
           data_file.name,
           (self.gnuplot_column_no.split(':')[0] if 'noerror' in self.request.GET and type(self.gnuplot_column_no) != int else self.gnuplot_column_no),
           ('w lines' if self.gnuplot_lines else ''),
           ('w errorbars' if ':' in str(self.gnuplot_column_no) and not 'noerror' in self.request.GET else ''),
           self.gnuplot_timefmt,
           self.gnuplot_ylabel
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
        context.update(self.kwargs)
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
                kwargs.update(year=dt.year,month=str(dt.month).zfill(2),day=str(dt.day).zfill(2))
                suffix = '_day'
            elif year:
                kwargs.update(year=dt.year,month=str(dt.month).zfill(2))
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

class NoPointsError(ValueError):
    pass

class PointsPlotView(PlotView, PointsView):
    plottype = ''
    sidplot = False
    gnuplot_column_no = '3:($3-$4):($3+$4)'
    gnuplot_ylabel = 'Flux'

    def get_data_file(self):
        data_file = tempfile.NamedTemporaryFile()
        inactive_only = 'inactive' in self.request.GET
        active_only = not 'all' in self.request.GET and not inactive_only 
        if len(self.object_list) == 0:
            raise NoPointsError()
        for point in self.object_list:
            if (self.model != RealPoint
             or (not active_only and not inactive_only)
             or (active_only and point.active)
             or (inactive_only and not point.active)):
                if self.model == RealPoint:
                    if self.sidplot:
                        if not point.sidpoint: continue
                        data_file.write(unicode(point.sidpoint.sidtime.time))
                    else:
                        data_file.write(unicode(point.image.datetime))
                else:
                    data_file.write(unicode(point.sidtime.time))
                data_file.write(' ')
                data_file.write(unicode(point.flux))
                data_file.write(' ')
                data_file.write(unicode(point.flux_error))
                data_file.write('\n')
                #print point.flux, point.flux_error
        data_file.flush()
        import shutil
        shutil.copyfile(data_file.name, '/home/bjwebb/clouds/tmpdata')
        return data_file

    def get_context_data(self, **context):
        if 'timestamp' in self.request.GET:
            context.update(timestamp=int(self.request.GET['timestamp'].split('.')[0]))
        context.update(line=self.kwargs['line'])
        return super(PointsPlotView, self).get_context_data(**context)

class RealPointsPlotView(DatePlotView, PointsPlotView):
    template_prefix = 'clouds.views.line_realpoints_plot'
    pass


class SidPlotView(PointsPlotView):
    gnuplot_timefmt='%H:%M:%S'
    gnuplot_date_format='%H:%M'
    gnuplot_column_no='2:($2-$3):($2+$3)'
    sidplot = True

    def get(self, request, hour=None, **kwargs):
        if 'timestamp' in request.GET and not hour:
            dt = datetime.datetime.fromtimestamp(float(self.request.GET['timestamp']))
            kwargs.update(hour=dt.time().hour)
            q = request.GET.copy()
            # 'day' here is misleading, but keeps compatibility with image views
            if 'day' in request.GET: 
                del q['day']
            else:
                del q['timestamp']
            return HttpResponseRedirect(reverse('clouds.views.line_sidpoints_plot_hour', kwargs=kwargs)+'?'+q.urlencode())
        if hour:
            self.extra_commands = """set xrange ['{0}:00':'{1}:00']""".format(int(hour), int(hour)+1)
        return super(SidPlotView, self).get(request, **kwargs)

class CloudsPlotView(DatePlotView, TemplateView):
    gnuplot_ylabel = 'Visibility'
    
    def get(self, request, *args, **kwargs):
        if 'column' in request.GET:
            self.gnuplot_column_no = int(request.GET['column'])

        return super(CloudsPlotView, self).get(request, *args, **kwargs)

    def get_data_file(self):
        if 'minpoints' in self.request.GET:
            minpoints = int(self.request.GET['minpoints'])
        else: minpoints = 200
        suffix = '-nomoon' if 'nomoon' in self.request.GET else '-hidemoon' if 'hidemoon' in self.request.GET else ''
        suffix += '-nofilter' if 'nofilter' in self.request.GET else ''
        datafilename = 'perimage-'+str(minpoints)+suffix+'-data' + ('_infsig' if 'infsig' in self.request.GET else '')
        return open(os.path.join(settings.MEDIA_ROOT, 'out', datafilename), 'r')

class AniView(ListView):
    template_name = 'clouds/ani.html'
    def get_queryset(self):
        kwargs = self.kwargs
        dt_from = datetime.datetime(int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        dt_to = dt_from + datetime.timedelta(days=1)
        return Image.objects.filter(datetime__gt=dt_from, datetime__lt=dt_to).order_by('datetime')


class DoubleViewMixin(object):
    gnuplot_size = '700,700'

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
    template_name = 'clouds/ani_plot_line.html'

    def get_context_data(self, **context):
        if 'zoom' in self.request.GET:
            self.extra_commands = """set xrange ['{0}':'{1}']""".format(
                    self.secondary_context_data['object_list'][0].image.datetime,
                    self.secondary_context_data['object_list'][-1].image.datetime)
            self.gnuplot_date_format = '%H:%M'
        return super(AniRealPointsPlotView, self).get_context_data(**context)

class AniSidPointsPlotView(DoubleViewMixin, SidPlotView):
    secondary_class = HourPointsView
    template_name = 'clouds/ani_plot_line.html'

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

    def get_queryset(self):
        queryset = super(ImageView, self).get_queryset()
        #queryset.prefetch_related('sidpoint', 'sidpoint__line', 'sidpoint__line__linevalues')
        return queryset


class RandomView(TemplateView):
    template_name = 'clouds/random.html'

    def get_context_data(self, **context):
        bins = []
#        for vmin,vmax in [ (0.0,0.01), (0.01, 0.05), (0.05, 0.1), (0.1,0.2), (0.2, 0.3), (0.3, 1.0) ] :
        for vmin,vmax in [ (0.0,0.03), (0.03, 0.15), (0.15, 0.3), (0.3,0.6), (0.6, 0.9), (0.9, 1.2) ] :
            images = Image.objects.filter(visibility__gte=vmin, visibility__lt=vmax)
            if 'hidemoon' in self.request.GET:
                images = images.filter(moon=False)
            if 'onlymoon' in self.request.GET:
                images = images.filter(moon=True)
            count = images.count()
            if count > 0:
                # http://stackoverflow.com/questions/9354127/how-to-grab-one-random-item-from-a-database-in-django-postgresql
                i = random.randint(0, count-1)
                image = images[i]
            else:
                image = None
            bins.append({'image': image, 'min':vmin, 'max':vmax, 'count':count})
        context['bins'] = bins
        return context

def lineimg(request, pk):
    im = PIL.Image.new('RGB', (640,480), 'white')
    draw = PIL.ImageDraw.Draw(im)
    line = Line.objects.get(pk=pk)
    prev_point = None
    for point in line.sidpoint_set.select_related('prev').all():
        prev_point = point.prev
        if type(prev_point) == type(None):
            draw.point((point.x, point.y), fill='black')
        else:
            draw.line((prev_point.x, prev_point.y, point.x, point.y), fill='black')
    from django.db import connection
    #print connection.queries
    if 'real' in request.GET:
        for point in line.realpoint_set.all():
            draw.point((point.x, point.y), fill='blue')
    output = StringIO.StringIO()
    im.save(output, format='PNG')
    return HttpResponse(output.getvalue(), 'image/png')

home = TemplateView.as_view(template_name='clouds/home.html')

lines = LineListView.as_view()
line = DetailView.as_view(model=Line)

line_sidpoints = PaginatedPointsView.as_view(model=SidPoint)
line_sidpoints_plot = SidPlotView.as_view(model=SidPoint)
line_sidpoints_plot_hour = AniSidPointsPlotView.as_view(model=SidPoint)

line_realpoints = PaginatedPointsView.as_view(model=RealPoint)
line_realpoints_plot = RealPointsPlotView.as_view(model=RealPoint)
line_realpoints_plot_day = AniRealPointsPlotView.as_view(model=RealPoint)
line_realpoints_sidplot = SidPlotView.as_view(model=RealPoint)

plot = CloudsPlotView.as_view()
ani = AniView.as_view()
plot_day = AniCloudsPlotView.as_view()

image = ImageView.as_view(model=Image)
sidtime = ImageView.as_view(model=SidTime, date_field='time')

random_view = RandomView.as_view()
random_view_tex = RandomView.as_view(template_name='clouds/random.tex')
