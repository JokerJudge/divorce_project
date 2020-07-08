from django.db import models

# Create your models here.
class Fiz_l(models.Model):
    #name = models.TextField()
    sex_choices = [('M', 'Мужской'), ('F', 'Женский')]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(default='2020-1-1')
    sex = models.CharField(max_length=1, choices=sex_choices, default='M')

    def __str__(self):
        return self.name



