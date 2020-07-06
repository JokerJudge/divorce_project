from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

# Create your views here.
class IndexView(View):
    def get(self, request):
        return render(request, 'divorce/index.html')

class DivorceView(View):
    def get(self, request):
        return render(request, 'divorce/divorce.html')
