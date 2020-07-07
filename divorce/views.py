from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse, HttpRequest
from .models import Fiz_l

# Create your views here.
class IndexView(View):
    def get(self, request):
        return render(request, 'divorce/index.html')

class DivorceView(View):
    def get(self, request):
        context = {'fiz_l_list': Fiz_l.objects.all()}
        return render(request, 'divorce/divorce.html', context)

def add_person(request:HttpRequest):
    # прочитать из input
    # content = request.POST['name']
    # create model for ORM
    # создать конструктор
    fiz_l = Fiz_l(name = request.POST['name'])
    fiz_l.save()
    return redirect('/divorce')

def del_person(request, person_id):
    person_to_delete = Fiz_l.objects.get(id=person_id)
    person_to_delete.delete()
    return redirect('/divorce')