from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from clouds.models import Line, SidPoint, RealPoint
from django.db.models import Count

def home(request):
    return HttpResponse('This page intentionally left blank.')

class LineListView(ListView):
    queryset = Line.objects.order_by('pk')
    paginate_by = 100

    def dispatch(self, request):
        if 'filter' in request.GET:
            if request.GET['filter'] == 'sid':
                self.queryset = self.queryset.annotate(Count('sidpoint')).filter(sidpoint__count__gt=20) 
            elif request.GET['filter'] == 'real':
                self.queryset = self.queryset.annotate(Count('realpoint')).filter(realpoint__count__gt=20) 
        return super(LineListView, self).dispatch(request)

class PointsView(ListView):
    paginate_by = 100
    template_name = 'clouds/point_list.html'

    def dispatch(self, request, line=None):
        self.queryset = self.model.objects.order_by('pk')
        if line:
            self.queryset = self.queryset.filter(line__pk=line)
        return super(PointsView, self).dispatch(request)

lines = LineListView.as_view()
line = DetailView.as_view(model=Line)

line_sidpoints = PointsView.as_view(model=SidPoint)
line_realpoints = PointsView.as_view(model=RealPoint)
