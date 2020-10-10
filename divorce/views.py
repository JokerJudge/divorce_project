from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.cache import cache
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import pickle
from django.http import HttpResponse, HttpRequest
from .models import Fiz_l, Marriage, Property, Distribution
from django.contrib.auth.models import User
from .forms import Fiz_l_form, Marriage_form, Marriage_form_divorce, Property_form, Distribution_form, SignUpForm
from divorce.law.marriage import marriage_law, person_edit_check
from divorce.law.property import form_1_processing, to_ownership, clean_coowners,\
    ownership_to_display, filter_for_distribution, transform_into_money, sum_money, change_distribution_property
from divorce.law.utils import Counter, digits_to_readable_property_list, digits_to_readable_distribution_property, digits_to_readable_money_sum

# Представление для основной страницы
class DivorceView(View):
    def get(self, request, property_id=0):
        if property_id == 0:
            cache_flag = cache.get('distribution_property_changed', None)
            if cache_flag is not None:
                cache.delete('distribution_property_changed')
                cache.delete('money_sum_initial')
                cache.delete('distribution_property_initial')
            # преобразовываем данные из БД в формат для вывода в divorce.html в колонке имущество
            property_to_display = ownership_to_display(Property.objects.filter(service_user_id=request.user.id))
            distribution = Distribution.objects.filter(service_user_id=request.user.id)
            distribution_names = {}
            distribution_property_str = {}
            money_sum_str = {}
            money_sum = {}
            #фильтруем имущество и записываем только то, которое принадлежит лицам, делящим имущество
            if property_to_display and distribution:
                distribution_property_1, distribution_names = filter_for_distribution(property_to_display, distribution)
                #cчитаем деньги (переводим доли в рубли)
                distribution_property = transform_into_money(distribution_property_1)
                # подсчитываем общее количество денег по имуществу
                money_sum, after_break_up = sum_money(distribution_property, distribution_names)
                # делаем читабельными цифры в представлении
                property_to_display = digits_to_readable_property_list(property_to_display)
                distribution_property_str = digits_to_readable_distribution_property(distribution_property)
                money_sum_str = digits_to_readable_money_sum(money_sum)
                #кэшируем вариант с цифрами в ценах, а не строки. Строки идут в представление
                cache.set('distribution_property_initial', distribution_property)
                cache.set('money_sum_initial', money_sum)

            num_visits = request.session.get('num_visits', 0)
            request.session['num_visits'] = num_visits + 1

            counter = Counter()
            context = {'fiz_l_list': Fiz_l.objects.filter(service_user_id=request.user.id),
                       'marriages_list': Marriage.objects.filter(service_user_id=request.user.id),
                       'property_raw': Property.objects.filter(service_user_id=request.user.id),
                       'property_list': property_to_display,
                       'counter': counter,
                       'distribution_list': Distribution.objects.filter(service_user_id=request.user.id),
                       'distribution_property': distribution_property_str,
                       'distribution_names': distribution_names,
                       'money_sum': money_sum_str,
                       'money_sum_digits': money_sum,
                       'num_visits': num_visits}
            return render(request, 'divorce/divorce.html', context)
        else:
            distribution_to = None
            change_to_private_after_break_up = False
            # если пошло по пути after_break_up
            if request.path.split('/')[-1] == 'after_break_up':
                change_to_private_after_break_up = True
            else:
                distribution_to = request.path.split('/')[-1]
            property_to_display = ownership_to_display(Property.objects.filter(service_user_id=request.user.id))
            distribution = Distribution.objects.filter(service_user_id=request.user.id)
            distribution_names = {}
            distribution_property = {}
            money_sum_str = {}
            money_sum = {}
            distribution_property_changed_str = {}
            # фильтруем имущество и записываем только то, которое принадлежит лицам, делящим имущество
            if property_to_display and distribution:
                cache_flag = cache.get('distribution_property_changed', None)
                if cache_flag is not None:
                    distribution_property_changed = cache.get('distribution_property_changed')
                    distribution_property_1, distribution_names = filter_for_distribution(property_to_display, distribution)
                    distribution_property_changed = change_distribution_property(distribution_property_changed,
                                                                                 distribution_names,
                                                                                 distribution_to,
                                                                                 property_id,
                                                                                 change_to_private_after_break_up,
                                                                                 request.GET)
                else:
                    distribution_property_1, distribution_names = filter_for_distribution(property_to_display, distribution)
                    # меняем собственников
                    distribution_property_changed = change_distribution_property(distribution_property_1,
                                                                                 distribution_names,
                                                                                 distribution_to,
                                                                                 property_id,
                                                                                 change_to_private_after_break_up,
                                                                                 request.GET)
                # cчитаем деньги (переводим доли в рубли)
                distribution_property_changed = transform_into_money(distribution_property_changed)
                # подсчитываем общее количество денег по имуществу
                money_sum_initial = cache.get('money_sum_initial')
                money_sum, after_break_up = sum_money(distribution_property_changed, distribution_names, property_id, money_sum_initial, change_to_private_after_break_up)
                money_sum_initial.update(after_break_up)
                # делаем читабельными цифры в представлении
                property_to_display = digits_to_readable_property_list(property_to_display)
                distribution_property_changed_str = digits_to_readable_distribution_property(distribution_property_changed)
                money_sum_str = digits_to_readable_money_sum(money_sum)
                # кэшируем вариант с цифрами в ценах, а не строки. Строки идут в представление
                cache.set('money_sum_initial', money_sum_initial)
                cache.set('distribution_property_changed', distribution_property_changed)
                distribution_property_initial = cache.get('distribution_property_initial')

            num_visits = request.session.get('num_visits', 0)
            request.session['num_visits'] = num_visits + 1

            counter = Counter()
            context = {'fiz_l_list': Fiz_l.objects.filter(service_user_id=request.user.id),
                       'marriages_list': Marriage.objects.filter(service_user_id=request.user.id),
                       'property_raw': Property.objects.filter(service_user_id=request.user.id),
                       'property_list': property_to_display,
                       'counter': counter,
                       'distribution_list': Distribution.objects.filter(service_user_id=request.user.id),
                       'distribution_property': distribution_property_changed_str,
                       'distribution_names': distribution_names,
                       'money_sum': money_sum_str,
                       'money_sum_digits': money_sum,
                       'num_visits': num_visits}
            return render(request, 'divorce/divorce.html', context)

# Представление для формы добавления/изменения сведений о физ.лице
class FizLFormView(LoginRequiredMixin, View):
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
                #print(f'проверки пройдены - {links}')
                user_dict = {'service_user_id': request.user.id}
                form.cleaned_data.update(user_dict)
                form.save()
                temp = form.save(commit=False)
                temp.service_user_id = form.cleaned_data['service_user_id']
                temp.save()
                return redirect('/divorce/')
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
    return redirect('/divorce/')

class MarriageFormView(LoginRequiredMixin, View):
    def get(self, request, id=0):
        if id == 0:
            form = Marriage_form()  # пустая форма
            #фильтруем только актуальные для пользователя варианты
            form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_marriage.html', {'form': form})
        else:  # update operation
            marriage = Marriage.objects.get(pk=id)
            form = Marriage_form(instance=marriage)  # заполненная имеющимися данными форма
            form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_marriage.html', {'form': form, 'marriage': marriage})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            form = Marriage_form(request.POST) # заполняем форму из словаря POST
            marriage = None
        else:
            marriage = Marriage.objects.get(pk=id)  # получаем по id нужный объект
            form = Marriage_form(request.POST, instance=marriage)  # marriage будет изменен новой формой request.POST

        if form.is_valid():
            # данные перед сохранением, но до обработки бизнес-логикой
            date_of_marriage_registration = form.cleaned_data['date_of_marriage_registration']
            parties = list(form.cleaned_data['parties'])
            person_1 = parties[0]
            person_2 = parties[1]
            resolution, link_list = marriage_law(person_1, person_2, date_of_marriage_registration, marriage)

            if resolution is True:
                links = [f'{i.link_name} - {i.law_link} {i.npa.short_title_for_link}' for i in link_list]
                #print(f'проверки пройдены - {links}')
                user_dict = {'service_user_id': request.user.id}
                form.cleaned_data.update(user_dict)
                form.save()
                temp = form.save(commit=False)
                temp.service_user_id = form.cleaned_data['service_user_id']
                temp.save()
                return redirect('/divorce/')
            else:
                errors = {
                    'Вид ошибки': link_list[-1].errors[0],
                    'Ссылка на норму': f'{link_list[-1].law_link} {link_list[-1].npa.short_title_for_link}',
                    'Текст нормы': link_list[-1].law_text
                }
                form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_marriage.html', {'form': form, 'errors': errors, 'marriage': marriage})
        # если есть проблемы с формой - ValueError из forms.py
        else:
            #фильтруем физ.лица для конкретного пользователя
            form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_marriage.html', {'form': form, 'marriage': marriage})

class MarriageFormDivorceView(LoginRequiredMixin, View):
    def get(self, request, id):
        marriage = Marriage.objects.get(pk=id)
        form = Marriage_form_divorce(instance=marriage) # показываем пустую форму / или форму с имеющимися данными
        return render(request, 'divorce/form_marriage_divorce.html', {'form': form, 'marriage': marriage})
    def post(self, request, id):
        marriage = Marriage.objects.get(pk=id)
        form = Marriage_form_divorce(request.POST, instance=marriage) # marriage будет изменен новой формой request.POST
        if form.is_valid():
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
            user_dict = {'service_user_id': request.user.id}
            form.cleaned_data.update(user_dict)
            form.save()
            temp = form.save(commit=False)
            temp.service_user_id = form.cleaned_data['service_user_id']
            temp.save()
            return redirect('/divorce/')
        else:
            return render(request, 'divorce/form_marriage_divorce.html', {'form': form, 'marriage': marriage})


def del_marriage(request, marriage_id):
    marriage_to_delete = Marriage.objects.get(id=marriage_id)
    marriage_to_delete.delete()
    return redirect('/divorce/')


class PropertyFormView(LoginRequiredMixin, View):
    def get(self, request, id=0):
        if id == 0:
            form = Property_form()  # пустая форма
            # фильтруем только актуальные для пользователя варианты
            form.fields['obtaining_person'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_property_1.html', {'form': form})
        else:  # update operation
            property = Property.objects.get(pk=id)
            form = Property_form(instance=property)  # заполненная имеющимися данными форма
            form.fields['obtaining_person'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_property_1.html', {'form': form, 'property': property, 'id': id})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            form = Property_form(request.POST) # заполняем форму из словаря POST
            property = None
        else:
            property = Property.objects.get(pk=id)  # получаем по id нужный объект
            form = Property_form(request.POST, instance=property)  # property будет изменен новой формой request.POST

        if form.is_valid():
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
            else:
                # получаем из брака родителей, которые необходимы, чтобы ответить на вопрос № 2 формы № 2
                list_of_parties = list(marriage.parties.all())
                parents = {}
                for i in list_of_parties:
                    if i.sex == 'М':
                        parents['father'] = i
                    else:
                        parents['mother'] = i
                cache.set('parents', parents)
                if id == 0:
                    return render(request,
                                  'divorce/form_property_2_m.html',
                                  {'form_1_processed_data': form_1_processed_data,
                                   'form_1': form.cleaned_data,
                                   'parents': parents})
                else:
                    #кэширую ID для внесения изменений в БД
                    cache.set('id', id)
                    return render(request,
                                  'divorce/form_property_2_m.html',
                                  {'form_1_processed_data': form_1_processed_data,
                                   'form_1': form.cleaned_data,
                                   'parents': parents})
        # если есть проблемы с формой - ValueError из forms.py
        else:
            form.fields['obtaining_person'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_property_1.html', {'form': form, 'property': property})

def del_property(request, property_id):
    property_to_delete = Property.objects.get(id=property_id)
    property_to_delete.delete()
    return redirect('/divorce/')


class PropertyForm2nmView(LoginRequiredMixin, View):
    '''
    Форма № 2 для варианта, когда приобретение имущества не совпало с браками
    '''
    def get(self, request, id=0):
        if id == 0:
            return render(request, 'divorce/form_property_2_nm.html')

        else:  # update operation
            property = Property.objects.get(pk=id)
            form = Property_form(instance=property)  # заполненная имеющимися данными форма
            return render(request, 'divorce/form_property_2_nm.html', {'form': form, 'property': property})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            # Фильтровка корректных значений, если есть сособственники
            if 'coowners' in request.POST:
                # проверка на правильность заполнения поля с долями
                errors = clean_coowners(request.POST)
                if errors:
                    return render(request, 'divorce/form_property_2_nm.html', {'errors': errors})

            # если всё хорошо:
            # выгружаем из кэша форму № 1 и обработанную форму
            # объединяем форму № 1, обработанную форму № 1, форму № 2 (request.POST) и self.ownership в form
            # для сохранения в БД
            form_full, form_1, form_1_processed_data = merging_forms(request.POST)
            # готовим форму № 2 к работе
            form_2 = request.POST
            ownership, list_of_links, for_child = to_ownership(form_full)
            # определяем пользователя, который добавляет имущество
            user_dict = {'service_user_id': request.user.id}
            # создаем новую форму, которая будет записана в БД
            form = Property_form(form_full)
            if form.is_valid(): # нужно обязательно вызвать метод is_valid - без него не появится словарь cleaned_data
                # обновляем словарь cleaned_data, так как часть сведений не валидировалась из формы, а получена из кэша
                form.cleaned_data.update(form_1_processed_data)
                form.cleaned_data.update(form_2)
                form.cleaned_data.update(ownership)
                form.cleaned_data.update(for_child)
                form.cleaned_data.update(user_dict)
                form.save()
                # Так как в форме type_of_property не валидировалась, то чтобы её записать в БД, нужно сохранить конкретную строку
                temp = form.save(commit=False)
                temp.type_of_property = form.cleaned_data['type_of_property']
                temp.for_child_accomodation = form.cleaned_data['child_accomodation']
                temp.after_break_up = form.cleaned_data['after_break_up']
                temp.ownership = form.cleaned_data['ownership']
                temp.service_user_id = form.cleaned_data['service_user_id']
                pick_own = pickle.dumps(form.cleaned_data['ownership'])
                temp.ownership_b = pick_own
                temp.save()
                # удаляем кэшированные данные
                cache.delete('form_1')
                cache.delete('form_1_processed_data')
                cache.delete('parents')
                return redirect('/divorce/')

        else:
            property = Property.objects.get(pk=id)  # получаем по id нужный объект

            if 'coowners' in request.POST:
                # проверка на правильность заполнения поля с долями
                errors = clean_coowners(request.POST)
                if errors == None:
                    pass
                else:
                    return render(request, f'divorce/form_property_2_nm.html', {'errors': errors})
            # если всё хорошо:
            # выгружаем из кэша форму № 1 и обработанную форму
            # объединяем форму № 1, обработанную форму № 1, форму № 2 (request.POST) и self.ownership в form
            # для сохранения в БД
            form_full, form_1, form_1_processed_data = merging_forms(request.POST)
            # готовим форму № 2 к работе
            form_2 = request.POST
            ownership, list_of_links, for_child = to_ownership(form_full)
            # создаем новую форму, которая будет записана в БД
            form = Property_form(form_full, instance=property)  # property будет изменен новой формой request.POST
            # определяем пользователя, который добавляет имущество
            user_dict = {'service_user_id': request.user.id}
            if form.is_valid(): # нужно обязательно вызвать метод is_valid - без него не появится словарь cleaned_data
                # обновляем словарь cleaned_data, так как часть сведений не валидировалась из формы, а получена из кэша
                form.cleaned_data.update(form_1_processed_data)
                form.cleaned_data.update(form_2)
                form.cleaned_data.update(ownership)
                form.cleaned_data.update(for_child)
                form.cleaned_data.update(user_dict)
                form.save()
                # Так как в форме type_of_property не валидировалась, то чтобы её записать в БД, нужно сохранить конкретную строку
                temp = form.save(commit=False)
                temp.type_of_property = form.cleaned_data['type_of_property']
                temp.for_child_accomodation = form.cleaned_data['child_accomodation']
                temp.after_break_up = form.cleaned_data['after_break_up']
                temp.ownership = form.cleaned_data['ownership']
                temp.service_user_id = form.cleaned_data['service_user_id']
                pick_own = pickle.dumps(form.cleaned_data['ownership'])
                temp.ownership_b = pick_own
                temp.save()
                # удаляем кэшированные данные
                cache.delete('form_1')
                cache.delete('form_1_processed_data')
                return redirect('/divorce/')


class PropertyForm2mView(LoginRequiredMixin, View):
    '''
    Форма № 2 для варианта, когда приобретение имущества совпало с браком
    '''
    def get(self, request, id=0):
        if id == 0:
            return render(request, 'divorce/form_property_2_m.html')

        else:  # update operation
            property = Property.objects.get(pk=id)
            form = Property_form(instance=property)  # заполненная имеющимися данными форма
            return render(request, 'divorce/form_property_2_m.html', {'form': form, 'property': property})

    def post(self, request, id=0):
        # Выгружаем из кэша id, если у нас идет процедура внесения изменений
        if cache.get('id') != None:
            id = cache.get('id')
        if id == 0:  # если данные пока не записаны в БД
            parents = cache.get('parents')
            # объединяем форму № 1, обработанную форму № 1, форму № 2 (request.POST) и self.ownership в form
            form_full, form_1, form_1_processed_data = merging_forms(request.POST)

            # проверка на сособственников (помимо супругов)
            # + проверка на правильность заполнения полей с долями (валидация долей)
            errors = clean_coowners(request.POST)
            if errors:
                return render(request, 'divorce/form_property_2_m.html', {'errors': errors,
                                                                              'form_1': form_1,
                                                                              'form_1_processed_data': form_1_processed_data,
                                                                              'parents': parents})

            # готовим форму № 2 к работе
            form_2 = request.POST
            ownership, list_of_links, for_child = to_ownership(form_full)
            # создаем новую форму, которая будет записана в БД
            form = Property_form(form_full)
            # определяем пользователя, который добавляет имущество
            user_dict = {'service_user_id': request.user.id}
            if form.is_valid(): # нужно обязательно вызвать метод is_valid - без него не появится словарь cleaned_data
                # обновляем словарь cleaned_data, так как часть сведений не валидировалась из формы, а получена из кэша
                form.cleaned_data.update(form_1_processed_data)
                form.cleaned_data.update(form_2)
                form.cleaned_data.update(ownership)
                form.cleaned_data.update(for_child)
                form.cleaned_data.update(user_dict)
                form.save()
                # Так как в форме type_of_property не валидировалась, то чтобы её записать в БД, нужно сохранить конкретную строку
                temp = form.save(commit=False)
                temp.type_of_property = form.cleaned_data['type_of_property']
                temp.for_child_accomodation = form.cleaned_data['child_accomodation']
                temp.after_break_up = form.cleaned_data['after_break_up']
                temp.ownership = form.cleaned_data['ownership']
                temp.service_user_id = form.cleaned_data['service_user_id']
                pick_own = pickle.dumps(form.cleaned_data['ownership'])
                temp.ownership_b = pick_own
                temp.save()
                # удаляем кэшированные данные
                cache.delete('form_1')
                cache.delete('form_1_processed_data')
                cache.delete('parents')
                return redirect('/divorce/')


        else:
            property = Property.objects.get(pk=id)  # получаем по id нужный объект
            parents = cache.get('parents')
            # объединяем форму № 1, обработанную форму № 1, форму № 2 (request.POST) и self.ownership в form
            form_full, form_1, form_1_processed_data = merging_forms(request.POST)

            errors = clean_coowners(request.POST)
            if errors:
                return render(request, 'divorce/form_property_2_m.html', {'errors': errors,
                                                                              'form_1': form_1,
                                                                              'form_1_processed_data': form_1_processed_data,
                                                                              'parents': parents})

            # готовим форму № 2 к работе
            form_2 = request.POST
            ownership, list_of_links, for_child = to_ownership(form_full)
            # создаем новую форму, которая будет записана в БД
            form = Property_form(form_full, instance=property)  # property будет изменен новой формой request.POST
            # определяем пользователя, который добавляет имущество
            user_dict = {'service_user_id': request.user.id}
            if form.is_valid(): # нужно обязательно вызвать метод is_valid - без него не появится словарь cleaned_data
                # обновляем словарь cleaned_data, так как часть сведений не валидировалась из формы, а получена из кэша
                form.cleaned_data.update(form_1_processed_data)
                form.cleaned_data.update(form_2)
                form.cleaned_data.update(ownership)
                form.cleaned_data.update(for_child)
                form.cleaned_data.update(user_dict)
                form.save()
                # Так как в форме type_of_property не валидировалась, то чтобы её записать в БД, нужно сохранить конкретную строку
                temp = form.save(commit=False)
                temp.type_of_property = form.cleaned_data['type_of_property']
                temp.for_child_accomodation = form.cleaned_data['child_accomodation']
                temp.after_break_up = form.cleaned_data['after_break_up']
                temp.ownership = form.cleaned_data['ownership']
                temp.service_user_id = form.cleaned_data['service_user_id']
                pick_own = pickle.dumps(form.cleaned_data['ownership'])
                temp.ownership_b = pick_own
                temp.save()
                # удаляем кэшированные данные
                cache.delete('form_1')
                cache.delete('form_1_processed_data')
                cache.delete('parents')
                cache.delete('id')
                return redirect('/divorce/')

def merging_forms(form: dict):
    '''
    Функция, которая соединяет все данные, которые пользователь передал в form_1 и form_2,
    а также данные, которые обработал python (form_1_processed_data)
    :param form: request.POST (формы 2)
    :return: соединенный словарь, кэшированная form_1 и кэшированная form_1_processed_data
    '''
    # выгружаем из кэша форму № 1 и обработанную форму
    form_1 = cache.get('form_1')
    form_1_processed_data = cache.get('form_1_processed_data')

    # готовим форму № 2 к работе
    form_2 = form
    # соединяем всё в один словарь
    form_example = form_1.copy()
    form_example.update(form_1_processed_data)
    form_example.update(form_2)
    return form_example, form_1, form_1_processed_data


class DistributionFormView(LoginRequiredMixin, View):
    def get(self, request, id=0):
        if id == 0:
            form = Distribution_form()  # пустая форма
            # фильтруем форму только актуальными для пользователя значениями
            form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_distribution.html', {'form': form})
        else:  # update operation
            distribution = Distribution.objects.get(pk=id)
            form = Distribution_form(instance=distribution)  # заполненная имеющимися данными форма
            form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_distribution.html', {'form': form, 'distribution': distribution})

    def post(self, request, id=0):
        if id == 0:  # если данные пока не записаны в БД
            form = Distribution_form(request.POST) # заполняем форму из словаря POST
            distribution = None
        else:
            distribution = Distribution.objects.get(pk=id)  # получаем по id нужный объект
            form = Marriage_form(request.POST, instance=distribution)  # distribution будет изменен новой формой request.POST

        user_dict = {'service_user_id': request.user.id}
        if form.is_valid():
            # данные перед сохранением, но до обработки бизнес-логикой
            form.cleaned_data.update(user_dict)
            form.save()
            temp = form.save(commit=False)
            temp.service_user_id = form.cleaned_data['service_user_id']
            temp.save()
            return redirect('/divorce/')

        # если есть проблемы с формой - ValueError из forms.py
        else:
            form.fields['parties'].queryset = Fiz_l.objects.filter(service_user_id=request.user.id)
            return render(request, 'divorce/form_distribution.html', {'form': form, 'distribution': distribution})


def del_distribution(request, distribution_id):
    distribution_to_delete = Distribution.objects.get(id=distribution_id)
    distribution_to_delete.delete()
    return redirect('/divorce/')

class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user('myusername', 'myemail@test.com', 'mypassword')
            user.username = form.cleaned_data.get('username')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.set_password(form.cleaned_data.get('password1'))
            user.check_password(form.cleaned_data.get('password1'))
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/divorce/')
        else:
            return render(request, 'registration/signup.html', {'form': form})


