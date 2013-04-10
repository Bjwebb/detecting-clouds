from django.http import HttpResponse
from views import NoPointsError

class HandleExceptions:
    def process_exception(self, request, exception):
        if type(exception) ==  NoPointsError:
            return HttpResponse('Could not create a plot, because there were no points.')
