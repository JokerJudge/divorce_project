from django.db import models

# Create your models here.
class Fiz_l(models.Model):
    sex_choices = [('М', 'Мужской'), ('Ж', 'Женский')]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(default='2020-1-1')
    sex = models.CharField(max_length=1, choices=sex_choices)
    #marriages = models.ManyToManyField('Marriage', blank=True, related_name='parties')

    def __str__(self):
        return self.name

class Marriage(models.Model):
    #party_m = models.ForeignKey(Fiz_l, on_delete=models.CASCADE)
    #party_f = models.ForeignKey(Fiz_l, on_delete=models.CASCADE)
    date_of_marriage_registration = models.DateField(default='2020-1-1')
    date_of_marriage_divorce = models.DateField(blank=True, null=True)
    date_of_break_up = models.DateField(blank=True, null=True)
    parties = models.ManyToManyField('Fiz_l', blank=True, related_name='marriages')

    def __str__(self):
        list_to_display = list(self.parties.all())
        if len(list_to_display) == 2:
            return f'Брак между {list_to_display[0]} и {list_to_display[1]}'
        else:
            return f'Брак указан некорректно'
