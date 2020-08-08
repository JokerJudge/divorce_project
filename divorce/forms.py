from django import forms
from django.core.exceptions import ValidationError #№7 25:25, 36:07, 43:33
from django.forms import ModelMultipleChoiceField

import datetime

from .models import Fiz_l, Marriage

class Fiz_l_form(forms.ModelForm):
    class Meta:
        model = Fiz_l
        # можно fields = '__all__'
        fields = ('name', 'date_of_birth', 'sex')
        labels = {
            'name': 'Имя',
            'date_of_birth': 'Дата рождения',
            'sex': 'Пол'
        }

    def clean_date_of_birth(self):
        '''
        Проверка на то, чтобы дата рождения была в пределах от 1900 года до 2050
        :return: отвалидированное значение date_of_birth
        '''
        date_of_birth = self.cleaned_data['date_of_birth']
        if date_of_birth < datetime.date(1900, 1, 1) or date_of_birth > datetime.date(2050, 1, 1):
            raise ValidationError('Введите дату в промежутке между 1900 годом и 2050 годом')
        else:
            return date_of_birth

    def __init__(self, *args, **kwargs):
        super(Fiz_l_form, self).__init__(*args, **kwargs)
        self.fields['sex'].empty_label = 'Укажите пол' # почему-то не работает
        # убрать обязательность поля
        #self.fields['sex'].required = False

class Marriage_form(forms.ModelForm):

    class Meta:
        model = Marriage
        # можно fields = '__all__'
        fields = ('date_of_marriage_registration', 'parties', 'date_of_marriage_divorce', 'date_of_break_up',)
        labels = {
            'date_of_marriage_registration': 'Дата регистрации брака',
            'parties': 'Стороны',
            'date_of_marriage_divorce': 'Дата расторжения брака',
            'date_of_break_up': 'Дата фактического прекращения брачных отношений (прекращение совместного проживания '
                                'и прекращение ведения совместного хозяйства)'
        }
        widgets = {
            'date_of_marriage_registration': forms.DateInput(),
            'parties': forms.CheckboxSelectMultiple(),
            'date_of_marriage_divorce': forms.DateInput(),
            'date_of_break_up': forms.DateInput(),
        }

    def clean_parties(self):
        '''
        Проверка на то, что пользователь выбрал именно 2 физ.лица для заключения брака
        :return: отвалидированное значение parties
        '''
        parties = self.cleaned_data['parties']
        if len(list(parties)) != 2:
            raise ValidationError('Нужно выбрать 2 лица')
        else:
            return parties

    def clean_date_of_marriage_divorce(self):
        '''
        Проверка, чтобы дата расторжения брака не была раньше даты заключения брака
        :return: отвалидированное значение date_of_marriage_divorce
        '''
        date_of_marriage_divorce = self.cleaned_data['date_of_marriage_divorce']
        # если есть запись о date_of_marriage_divorce
        if date_of_marriage_divorce is not None:
            date_of_marriage_registration = self.cleaned_data['date_of_marriage_registration']
            if date_of_marriage_divorce <= date_of_marriage_registration:
                raise ValidationError('Брак не может быть расторгнут ранее его заключения')
        return date_of_marriage_divorce

    def clean_date_of_break_up(self):
        '''
        Проверка, чтобы дата фактического прекращения брачных отношений была не ранее даты регистрации
        брака (date_of_marriage_registration) и не позже даты расторжения брака (date_of_marriage_divorce)
        :return: отвалидированное значение date_of_break_up
        '''
        date_of_break_up = self.cleaned_data['date_of_break_up']
        if date_of_break_up is not None:
            date_of_marriage_registration = self.cleaned_data['date_of_marriage_registration']
            if date_of_break_up <= date_of_marriage_registration:
                raise ValidationError('Прекращение отношений не может наступить ранее заключения брака')
            date_of_marriage_divorce = self.cleaned_data['date_of_marriage_divorce']
            if date_of_marriage_divorce is not None:
                if date_of_marriage_divorce < date_of_break_up:
                    raise ValidationError('Прекращение отношений не может наступить позднее даты прекращения брака')
        return date_of_break_up

class Marriage_form_divorce(forms.ModelForm):
    class Meta:
        model = Marriage
        fields = ('date_of_marriage_divorce', 'date_of_break_up',)
        labels = {
            'date_of_marriage_divorce': 'Дата регистрации развода',
            'date_of_break_up': 'Дата фактического прекращения брачных отношений (прекращение совместного проживания '
                                'и прекращение ведения совместного хозяйства)'
        }
        widgets = {
            'date_of_marriage_divorce': forms.DateInput(),
            'date_of_break_up': forms.DateInput(),
        }

    def clean_date_of_break_up(self):
        '''
        Проверка, чтобы дата фактического прекращения брачных отношений была не ранее даты регистрации
        брака (date_of_marriage_registration) и не позже даты расторжения брака (date_of_marriage_divorce)
        :return: отвалидированное значение date_of_break_up
        '''
        date_of_break_up = self.cleaned_data['date_of_break_up']
        date_of_marriage_divorce = self.cleaned_data['date_of_marriage_divorce']
        if date_of_break_up is not None and date_of_marriage_divorce is not None:
            print()
            print('++++++++++++!!!!!!!!!!!!!')
            print('Я тут!!')
            print()
            # date_of_marriage_registration = Marriage.objects.get() self.cleaned_data['date_of_marriage_registration']
            # if date_of_break_up <= date_of_marriage_registration:
            #     raise ValidationError('Прекращение отношений не может наступить ранее заключения брака')
            print(date_of_marriage_divorce)
            print(date_of_break_up)
            if date_of_marriage_divorce < date_of_break_up:
                print()
                print('++++++++++++!!!!!!!!!!!!!')
                print('Теперь я тут!!')
                print()
                raise ValidationError('Прекращение отношений не может наступить позднее даты прекращения брака')
        return date_of_break_up
