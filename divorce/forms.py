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
        fields = ('date_of_marriage_registration', 'parties', 'date_of_marriage_divorce',)
        labels = {
            'date_of_marriage_registration': 'Дата регистрации брака',
            'parties': 'Стороны',
            'date_of_marriage_divorce': 'Дата расторжения брака'
        }
        widgets = {
            'date_of_marriage_registration': forms.DateInput(),
            'parties': forms.CheckboxSelectMultiple(),
            'date_of_marriage_divorce': forms.DateInput(),
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
        date_of_marriage_divorce = self.cleaned_data['date_of_marriage_divorce']
        # если есть запись о date_of_marriage_divorce
        if date_of_marriage_divorce is not None:
            date_of_marriage_registration = self.cleaned_data['date_of_marriage_registration']
            if date_of_marriage_divorce <= date_of_marriage_registration:
                raise ValidationError('Брак не может быть расторгнут ранее его заключения')
        return date_of_marriage_divorce


class Marriage_form_divorce(forms.ModelForm):
    class Meta:
        model = Marriage
        fields = ('date_of_marriage_divorce', )
        labels = {
            'date_of_marriage_divorce': 'Дата регистрации развода'
        }
        widgets = {
            'date_of_marriage_divorce': forms.DateInput(),
        }
