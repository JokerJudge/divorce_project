import datetime
import dateutil.relativedelta as relativedelta
from ..models import *
from .law import *
from .links_and_texts import *
'''
модуль делающий проверки в соответствии с законодательством РФ
для добавления имущества в базу данных
'''

def form_1_processing(cleaned_data: dict):
    '''
    Функция, обрабатывающая валидные значения формы № 1 при добавлении имущества.
    Формирует список дополнительных вопросов, которые должны быть отражены в форме № 2 для завершения добавления
    имущества.
    :param cleaned_data: словарь очищенных данных для модуля Property(name, type_of_property_form,
    date_of_purchase, obtaining_person, price
    :return: # TODO - нужно понять, что мне надо. Видимо, выбор из константных вопросов
    '''
    #name = cleaned_data['name']
    type_of_property_form = cleaned_data['type_of_property_form']
    date_of_purchase = cleaned_data['date_of_purchase']
    obtaining_person = cleaned_data['obtaining_person']
    #price = cleaned_data['price']

    type_of_property = type_of_property_func(type_of_property_form)
    print(type_of_property)
    pass

def type_of_property_func(type_of_property_form):
    '''
    Функция, преобразующая введенный пользователем тип имущества в вид имущества по ст. 128 ГК РФ
    :param type_of_property_form: выбранный пользователем вид имущества
    :return: вид имущества в соответствии со ст. 128 ГК РФ (Объекты прав)
    '''
    link_name, law_link, law_text, npa = TEXTS['type_of_property_func']
    link = Link(link_name, law_link, law_text, npa)

    nedvizhimost = ['Квартира', 'Дом с земельным участком', 'Иная недвижимая вещь']
    dvizhimoe_imushestvo = ['Автомобиль', 'Деньги наличные', 'Деньги безналичные', 'Иная движимая вещь']
    if type_of_property_form in nedvizhimost:
        type_of_property = 'Недвижимость'
    elif type_of_property_form in dvizhimoe_imushestvo:
        type_of_property = 'Движимое имущество'
    #лишний else
    else:
        type_of_property = None
    return type_of_property

'''
К объектам гражданских прав относятся вещи (включая наличные деньги и документарные ценные бумаги), 
иное имущество, в том числе имущественные права (включая безналичные денежные средства, бездокументарные 
ценные бумаги, цифровые права); результаты работ и оказание услуг; охраняемые результаты интеллектуальной
 деятельности и приравненные к ним средства индивидуализации (интеллектуальная собственность); нематериальные
  блага

'''
'''

        type_of_property_choices = [('Квартира', 'Квартира'),
                                    ('Дом c земельным участком', 'Дом с земельным участком'),
                                    ('Автомобиль', 'Автомобиль'),
                                    ('Деньги наличные', 'Деньги наличные'),
                                    ('Деньги безналичные', 'Деньги безналичные'),
                                    ('Иная недвижимая вещь', 'Иная недвижимая вещь'),
                                    ('Иная движимая вещь', 'Иная движимая вещь')]
'''
