from django.db import models
from divorce.law.links_and_texts import PURCHASE_TYPE_CHOICES, TYPES_OF_PROPERTY_CHOICES

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

class Property(models.Model):
    name = models.CharField(max_length=200)
    type_of_property_form = models.CharField(max_length=50, choices=TYPES_OF_PROPERTY_CHOICES)
    type_of_property = models.CharField(max_length=100, blank=True, null=True)
    date_of_purchase = models.DateField()
    ownership_b = models.BinaryField(blank=True, null=True)
    ownership = models.TextField(blank=True, null=True)
    purchase_type = models.CharField(max_length=30, choices=PURCHASE_TYPE_CHOICES, blank=True, null=True)
    obtaining_person = models.ForeignKey(Fiz_l, on_delete=models.CASCADE)
    source_of_purchase = models.ManyToManyField('Fiz_l', blank=True, related_name='property_source')
    price = models.PositiveIntegerField(default=0)
    pay_before_marriage = models.BooleanField(default=False)
    for_child_accomodation = models.CharField(max_length=200, blank=True, null=True)
    individual_use_party = models.CharField(max_length=200, blank=True, null=True)
    after_break_up = models.BooleanField(default=False)
    for_child = models.BooleanField(default=False)
    individual_use = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Distribution(models.Model):
    date_of_distribution = models.DateField()
    parties = models.ManyToManyField('Fiz_l', blank=True, related_name='distribution')

    def __str__(self):
        list_to_display = list(self.parties.all())
        if len(list_to_display) == 2:
            return f'{list_to_display[0]} и {list_to_display[1]} - раздел имущества'
        else:
            return f'Раздел имущества указан некорректно'