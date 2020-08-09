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
    :param cleaned_data: словарь очищенных данных для модуля Property(type_of_property_form,
    date_of_purchase, obtaining_person)
    :return: # TODO - нужно понять, что мне надо. Видимо, выбор из константных вопросов
    '''
    #name = cleaned_data['name']
    type_of_property_form = cleaned_data['type_of_property_form']
    date_of_purchase = cleaned_data['date_of_purchase']
    obtaining_person = cleaned_data['obtaining_person']
    #price = cleaned_data['price']

    list_of_links = []
    # на основании введенного пользователем вида имущества - указываем вид имущества в соответствии со ст. 128 ГК РФ
    type_of_property, link = type_of_property_func(type_of_property_form)
    list_of_links.append(link)

    # проверяем дату покупки на пересечение с браками выбранного лица (obtaining_person)
    # TODO
    print(type_of_property, link)
    pass

def type_of_property_func(type_of_property_form):
    '''
    Функция, преобразующая введенный пользователем тип имущества в вид имущества по ст. 128 ГК РФ
    :param type_of_property_form: выбранный пользователем вид имущества
    :return: вид имущества в соответствии со ст. 128 ГК РФ (Объекты прав)
    '''
    link_name, law_link, law_text, npa = TEXTS['type_of_property_func']
    link = Link(link_name, law_link, law_text, npa)

    if type_of_property_form in OBJECTS_OF_CIVIL_LAW['NEDVIZHIMOST']:
        type_of_property = 'Недвижимая вещь'
    elif type_of_property_form in OBJECTS_OF_CIVIL_LAW['DVIZHIMAYA_VESH']:
        type_of_property = 'Движимая вещь'
    elif type_of_property_form in OBJECTS_OF_CIVIL_LAW['RID']:
        type_of_property = 'Исключительное право'
    elif type_of_property_form in OBJECTS_OF_CIVIL_LAW['INOE_IMUSHESTVO']:
        type_of_property = 'Иное имущество'
    #лишний else
    else:
        type_of_property = None
    return type_of_property, link
