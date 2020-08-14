from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest
from .models import Fiz_l, Marriage, Property
from .forms import Fiz_l_form, Marriage_form, Marriage_form_divorce, Property_form
from divorce.law.marriage import marriage_law, person_edit_check
from divorce.law.property import form_1_processing, to_ownership, clean_coowners

# Create your views here.
# Представление для основной страницы
class DivorceView(View):
    def get(self, request):
        context = {'fiz_l_list': Fiz_l.objects.all(),
                   'marriages_list': Marriage.objects.all(),
                   'property_list': Property.objects.all()}
        return render(request, 'divorce/divorce.html', context)

# Представление для формы добавления/изменения сведений о физ.лице
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
            person = None
        else:
            person = Fiz_l.objects.get(pk=id)  # получаем по id нужный объект
            form = Fiz_l_form(request.POST, instance=person)  # person будет изменен новой формой request.POST
        if form.is_valid():
            resolution, link_list = person_edit_check(person)
            if resolution is True:
                links = [f'{i.link_name} - {i.law_link} {i.npa.short_title_for_link}' for i in link_list]
                print(f'проверки пройдены - {links}')
                form.save()
                return redirect('/divorce')
            else:
                errors = {
                    'Вид ошибки': link_list[-1].errors[0],
                    'Ссылка на норму': f'{link_list[-1].law_link} {link_list[-1].npa.short_title_for_link}',
                    'Текст нормы': link_list[-1].law_text
                }
            return render(request, 'divorce/form_fiz_l.html', {'form': form, 'errors': errors})

        else:
            return render(request, 'divorce/form_fiz_l.html', {'form': form})

# Контроллер для удаления физ.лица
def del_person(request, person_id):
    person_to_delete = Fiz_l.objects.get(id=person_id)
    # проверка на наличие браков и их удаление
    for i in list(person_to_delete.marriages.all()): #Fiz_l.marriages.all() - все браки Fiz_l
        i.delete()
    person_to_delete.delete()
    return redirect('/divorce')

class MarriageFormView(View):
    def get(self, request, id=0):
        if id == 0:
            form = Marriage_form()  # пустая форма
            return render(request, 'divorce/form_marriage.html', {'form': form})
        else:  # update operation
            marriage = Marriage.objects.get(pk=id)
            form = Marriage_form(instance=marriage)  # заполненная имеющимися данными форма
            return render(request, 'divorce/form_marriage.html', {'form': form, 'marriage': marriage})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            form = Marriage_form(request.POST) # заполняем форму из словаря POST
            marriage = None
        else:
            marriage = Marriage.objects.get(pk=id)  # получаем по id нужный объект
            form = Marriage_form(request.POST, instance=marriage)  # marriage будет изменен новой формой request.POST

        if form.is_valid():
            print('+++++++++++cleaned_data+++++++++++++++++++')
            print(form.cleaned_data)
            # данные перед сохранением, но до обработки бизнес-логикой
            date_of_marriage_registration = form.cleaned_data['date_of_marriage_registration']
            parties = list(form.cleaned_data['parties'])
            person_1 = parties[0]
            person_2 = parties[1]
            print(date_of_marriage_registration)
            print(person_1)
            print(person_2)
            resolution, link_list = marriage_law(person_1, person_2, date_of_marriage_registration, marriage)

            if resolution is True:
                links = [f'{i.link_name} - {i.law_link} {i.npa.short_title_for_link}' for i in link_list]
                print(f'проверки пройдены - {links}')
                form.save()
                return redirect('/divorce')
            else:
                errors = {
                    'Вид ошибки': link_list[-1].errors[0],
                    'Ссылка на норму': f'{link_list[-1].law_link} {link_list[-1].npa.short_title_for_link}',
                    'Текст нормы': link_list[-1].law_text
                }
            return render(request, 'divorce/form_marriage.html', {'form': form, 'errors': errors, 'marriage': marriage})
        # если есть проблемы с формой - ValueError из forms.py
        else:
            return render(request, 'divorce/form_marriage.html', {'form': form, 'marriage': marriage})


class MarriageFormDivorceView(View):
    def get(self, request, id):
        marriage = Marriage.objects.get(pk=id)
        form = Marriage_form_divorce(instance=marriage) # показываем пустую форму / или форму с имеющимися данными
        return render(request, 'divorce/form_marriage_divorce.html', {'form': form, 'marriage': marriage})
    def post(self, request, id):
        marriage = Marriage.objects.get(pk=id)
        form = Marriage_form_divorce(request.POST, instance=marriage) # marriage будет изменен новой формой request.POST
        if form.is_valid():
            print('+++++++++++cleaned_data+++++++++++++++++++')
            print(form.cleaned_data)
            # данные перед сохранением, но до обработки бизнес-логикой
            date_of_divorce = form.cleaned_data['date_of_marriage_divorce']
            date_of_break_up = form.cleaned_data['date_of_break_up']
            date_of_marriage_registration = marriage.date_of_marriage_registration
            if date_of_divorce is not None:
                if date_of_divorce <= date_of_marriage_registration:
                    errors = {
                        'Дата развода не может быть ранее даты заключения брака': f'{date_of_marriage_registration}'
                    }
                    return render(request, 'divorce/form_marriage_divorce.html',
                                  {'form': form, 'marriage': marriage, 'errors': errors})
            if date_of_break_up is not None:
                if date_of_break_up < date_of_marriage_registration:
                    errors = {
                        'Дата прекращения брачных отношений не может быть раньше заключения брака': f'{date_of_marriage_registration}'
                    }
                    return render(request, 'divorce/form_marriage_divorce.html', {'form': form, 'marriage': marriage, 'errors': errors})
            print(marriage)
            print(date_of_divorce)
            form.save()
            return redirect('/divorce')
        else:
            return render(request, 'divorce/form_marriage_divorce.html', {'form': form, 'marriage': marriage})


def del_marriage(request, marriage_id):
    marriage_to_delete = Marriage.objects.get(id=marriage_id)
    marriage_to_delete.delete()
    return redirect('/divorce')


class PropertyFormView(View):
    def get(self, request, id=0):
        if id == 0:
            form = Property_form()  # пустая форма
            return render(request, 'divorce/form_property_1.html', {'form': form})
        else:  # update operation
            property = Property.objects.get(pk=id)
            form = Property_form(instance=property)  # заполненная имеющимися данными форма
            return render(request, 'divorce/form_property_1.html', {'form': form, 'property': property, 'id': id})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            form = Property_form(request.POST) # заполняем форму из словаря POST
            property = None
        else:
            property = Property.objects.get(pk=id)  # получаем по id нужный объект
            form = Property_form(request.POST, instance=property)  # property будет изменен новой формой request.POST

        if form.is_valid():
            print('+++++++++++cleaned_data+++++++++++++++++++')
            print(form.cleaned_data)
            # кэшируем полученные данные
            cache.set('form_1', form.cleaned_data)
            # обработка формы № 1
            type_of_property, marriage, after_break_up, list_of_links = form_1_processing(form.cleaned_data)

            form_1_processed_data = {'type_of_property': type_of_property,
                                     'marriage': marriage,
                                     'after_break_up': after_break_up,
                                     'list_of_links': list_of_links}
            # кэшируем обработанные данные
            cache.set('form_1_processed_data', form_1_processed_data)

            if marriage is None:
                if id == 0:
                    return redirect('/divorce/form_property_2_nm')
                else:
                    return redirect(f'/divorce/form_property_2_nm/{id}')
                #return render(request, 'divorce/form_property_2_nm.html', {'form': form, 'property': property, 'form_1': form_1})
            else:
                # TODO - если есть брак
                return render(request, 'divorce/form_property_2_m.html',
                              {'form': form, 'property': property, 'form_1': form_1})

            #return redirect('/divorce')
        # если есть проблемы с формой - ValueError из forms.py
        else:
            return render(request, 'divorce/form_property_1.html', {'form': form, 'property': property})

def del_property(request, property_id):
    property_to_delete = Property.objects.get(id=property_id)
    property_to_delete.delete()
    return redirect('/divorce')


class PropertyForm2nmView(View):
    '''
    Форма № 2 для варианта, когда приобретение имущества не совпало с браками
    '''
    def get(self, request, id=0):
        if id == 0:
            print()
            print('Я тут ОДИН!!!!')
            print()
            return render(request, 'divorce/form_property_2_nm.html')

        else:  # update operation
            print()
            print('Я тут ДВА!!!!')
            print()
            property = Property.objects.get(pk=id)
            form = Property_form(instance=property)  # заполненная имеющимися данными форма
            return render(request, 'divorce/form_property_2_nm.html', {'form': form, 'property': property})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            print()
            print('Я тут ТРИ!!!!')
            print()
            # Фильтровка корректных значений, если есть сособственники
            if 'coowners' in request.POST:
                # проверка на правильность заполнения поля с долями
                errors = clean_coowners(request.POST)
                if errors == None:
                    pass
                else:
                    return render(request, 'divorce/form_property_2_nm.html', {'errors': errors})
            # если всё хорошо:

            # грузим из кэша форму № 1 и обработанную форму
            # объединяем форму № 1, обработанную форму № 1, форму № 2 (request.POST) и self.ownership в form
            # для сохранения в БД
            form_full, form_1, form_1_processed_data = merging_forms(request.POST)
            # готовим форму № 2 к работе
            form_2 = request.POST
            # TODO - готовим self.ownership (доделывать по мере заполнения видов имущества)
            ownership = to_ownership(form_full)
            # создаем новую форму, которая будет записана в БД
            form = Property_form(form_full)
            if form.is_valid(): # нужно обязательно вызвать метод is_valid - без него не появится словарь cleaned_data
                # обновляем руками словать cleaned_data, так как часть сведений не валидировалась из формы, а получена из кэша
                form.cleaned_data.update(form_1_processed_data)
                form.cleaned_data.update(form_2)
                form.cleaned_data.update(ownership)
                # Так как в форме type_of_property не валидировалась, то чтобы её записать в БД, нужно
                # ручками сохранить конкретную строку
                temp = form.save(commit=False)
                temp.type_of_property = form.cleaned_data['type_of_property']
                temp.ownership = form.cleaned_data['ownership']
                temp.save()
                # удаляем кэшированные данные
                cache.delete('form_1')
                cache.delete('form_1_processed_data')
                return redirect('/divorce')


            # вариант № 1 - нет сособственников - личная собственность
            # вариант № 2 - есть сособственники - долевая собственность

          #form = Property_form(request.POST) # заполняем форму из словаря POST
            #property = None
        else:
            print()
            print('Я тут ЧЕТЫРЕ!!!!')
            print()
            property = Property.objects.get(pk=id)  # получаем по id нужный объект
            #form = Property_form(request.POST, instance=property)  # property будет изменен новой формой request.POST

            if 'coowners' in request.POST:
                # проверка на правильность заполнения поля с долями
                errors = clean_coowners(request.POST)
                if errors == None:
                    pass
                else:
                    return render(request, f'divorce/form_property_2_nm.html', {'errors': errors})
            # если всё хорошо:
            # грузим из кэша форму № 1 и обработанную форму
            # объединяем форму № 1, обработанную форму № 1, форму № 2 (request.POST) и self.ownership в form
            # для сохранения в БД
            form_full, form_1, form_1_processed_data = merging_forms(request.POST)
            # готовим форму № 2 к работе
            form_2 = request.POST
            # TODO - готовим self.ownership (доделывать по мере заполнения видов имущества)
            ownership = to_ownership(form_full)
            # создаем новую форму, которая будет записана в БД
            form = Property_form(form_full, instance=property)  # property будет изменен новой формой request.POST
            #form = Property_form(form_example)
            if form.is_valid(): # нужно обязательно вызвать метод is_valid - без него не появится словарь cleaned_data
                # обновляем руками словать cleaned_data, так как часть сведений не валидировалась из формы, а получена из кэша
                form.cleaned_data.update(form_1_processed_data)
                form.cleaned_data.update(form_2)
                form.cleaned_data.update(ownership)
                # Так как в форме type_of_property не валидировалась, то чтобы её записать в БД, нужно
                # ручками сохранить конкретную строку
                temp = form.save(commit=False)
                temp.type_of_property = form.cleaned_data['type_of_property']
                temp.ownership = form.cleaned_data['ownership']
                temp.save()
                # удаляем кэшированные данные
                cache.delete('form_1')
                cache.delete('form_1_processed_data')
                return redirect('/divorce')

def merging_forms(form: dict):
    '''
    Функция, которая соединяет все данные, которые пользователь передал в form_1 и form_2,
    а также данные, которые обработал python (form_1_processed_data)
    :param form: request.POST (формы 2)
    :return: соединенный словарь, кэшированная form_1 и кэшированная form_1_processed_data
    '''
    # грузим из кэша форму № 1 и обработанную форму
    form_1 = cache.get('form_1')
    form_1_processed_data = cache.get('form_1_processed_data')

    # готовим форму № 2 к работе
    form_2 = form
    # сливаем всё в один словарь
    form_example = form_1.copy()
    form_example.update(form_1_processed_data)
    form_example.update(form_2)
    return form_example, form_1, form_1_processed_data

########################################################
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

