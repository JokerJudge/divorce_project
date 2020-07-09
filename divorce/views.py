from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse, HttpRequest
from .models import Fiz_l
from .forms import Fiz_l_form

# Create your views here.
class DivorceView(View):
    def get(self, request):
        context = {'fiz_l_list': Fiz_l.objects.all()}
        return render(request, 'divorce/divorce.html', context)

class FizLFormView(View):
    def get(self, request, id=0):
        if id == 0:
            form = Fiz_l_form()  # пустая форма
            return render(request, 'divorce/form_fiz_l.html', {'form': form})
        else: # update operation
            person = Fiz_l.objects.get(pk=id)
            form = Fiz_l_form(instance=person)  # заполненная имеющимися данными форма
            return render(request, 'divorce/form_fiz_l.html', {'form': form})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            form = Fiz_l_form(request.POST)
        else:
            person = Fiz_l.objects.get(pk=id)  # получаем по id нужный объект
            form = Fiz_l_form(request.POST, instance=person)  # person будет изменен новой формой request.POST
        if form.is_valid():
            form.save()
            return redirect('/divorce')


# def fiz_l_form_add(request, id=0):
#     if request.method == "GET":
#         if id == 0: #insert operation
#             form = Fiz_l_form() # пустая форма
#             return render(request, 'divorce/form_fiz_l.html', {'form': form})
#         else: #update operation
#             person = Fiz_l.objects.get(pk=id)
#             form = Fiz_l_form(instance=person) # заполненная имеющимися данными форма
#             return render(request, 'divorce/form_fiz_l.html', {'form': form})
#
#     else:
#         if id == 0: # если данные пока не записаны в БД
#             form = Fiz_l_form(request.POST)
#         else:
#             person = Fiz_l.objects.get(pk=id) # получаем по id нужный объект
#             form = Fiz_l_form(request.POST, instance=person) #person будет изменен новой формой request.POST
#         if form.is_valid():
#             form.save()
#             return redirect('/divorce')

# def add_person(request:HttpRequest):
#     # прочитать из input
#     # content = request.POST['name']
#     # create model for ORM
#     # создать конструктор
#     fiz_l = Fiz_l(name = request.POST['name'])
#     fiz_l.save()
#     return redirect('/divorce')

def del_person(request, person_id):
    person_to_delete = Fiz_l.objects.get(id=person_id)
    person_to_delete.delete()
    return redirect('/divorce')