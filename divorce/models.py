from django.db import models

# Create your models here.
class Fiz_l(models.Model):
    sex_choices = [('М', 'Мужской'), ('Ж', 'Женский')]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(default='2020-1-1')
    sex = models.CharField(max_length=1, choices=sex_choices)

    def __str__(self):
        return self.name

class Marriage(models.Model):
    #party_m = models.ForeignKey(Fiz_l, on_delete=models.CASCADE)
    #party_f = models.ForeignKey(Fiz_l, on_delete=models.CASCADE)
    date_of_marriage_registration = models.DateField(default='2020-1-1')
    date_of_marriage_divorce = models.DateField(blank=True, null=True)
    parties = models.ManyToManyField(Fiz_l)

    def __str__(self):
        list_to_display = list(self.parties.values()) # QuerySet в list
        names = []
        for i in list_to_display:
            names.append(i['name']) # выводим имена
            return f'Брак между {names[0]} и '



# при модели Many_to_Many
# return f'Брак между {self.parties.values().get(id=20)["name"]}' - первый вариант
# второй вариант
#    def __str__(self):
#        list_to_display = list(self.parties.values()) # QuerySet в list
#        names = []
#        for i in list_to_display:
#            names.append(i['name']) # выводим имена
#        return f'Брак между {names[0]} и '

