from django import forms
from django.forms import ModelMultipleChoiceField
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

    def __init__(self, *args, **kwargs):
        super(Fiz_l_form, self).__init__(*args, **kwargs)
        self.fields['sex'].empty_label = 'Укажите пол' # почему-то не работает
        # убрать обязательность поля
        #self.fields['sex'].required = False

class Marriage_form(forms.ModelForm):

    class Meta:
        model = Marriage
        # можно fields = '__all__'
        fields = ('date_of_marriage_registration', 'parties')
        labels = {
            'date_of_marriage_registration': 'Дата регистрации брака',
            'parties': 'Стороны'
        }
        widgets = {
            'date_of_marriage_registration': forms.DateInput(),
            'parties': forms.CheckboxSelectMultiple(),
        }

