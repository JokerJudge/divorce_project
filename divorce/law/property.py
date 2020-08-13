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
    :return: тип имущества в соответствии со ст. 128 ГК РФ (type_of_property), пересекающийся с покупкой брак (marriage),
    указание на то, произошло ли приобретение имущества после фактического прекращения брачных отношений
    (after_break_up), список ссылок на НПА (list_of_links)
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
    marriage, after_break_up, link_list = marriage_periods(obtaining_person, date_of_purchase) # link_list
    list_of_links.extend(link_list)
    return type_of_property, marriage, after_break_up, list_of_links


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

def marriage_periods(obtaining_person: Fiz_l, date_of_purchase: datetime.date):
    '''
    Функция, сопоставляющая дату приобретения имущества и наличие браков у лица, которое приобрело имущество
    :param obtaining_person: лицо, указанное пользователем как приобретатель имущества
    :return: marriage, after_break_up, list_of_links
    где:
    marriage - Marriage (если есть) или None (если нет)
    after_break_up - True (если приобретено имущество в браке, но после фактического прекращения брачных отношений) или
        False (в других случаях)
    list_of_links - список Link, по которым прошлась логика
    '''
    list_of_links = []
    link_name, law_link, law_text, npa = TEXTS['marriage_periods']
    link = Link(link_name, law_link, law_text, npa)
    list_of_links.append(link)

    marriage = None
    after_break_up = False #after_break_up in marriage

    if list(obtaining_person.marriages.all()):
        marriages = list(obtaining_person.marriages.all())
        for i in marriages:
            # проверка на приобретение после заключения брака
            if i.date_of_marriage_registration <= date_of_purchase:
                # проверка на то, что брак к моменту приобретения уже завершился
                if i.date_of_marriage_divorce is not None:
                    if i.date_of_marriage_divorce <= date_of_purchase:
                        continue # переходим к следующему браку
                    # приобретение произошло в период между заключением брака и расторжением брака
                    else:
                        # проверка на наличие факта прекращения брачных отношений
                        if i.date_of_break_up is not None:
                            # проверка на то, что приобретение произошло в период между фактическим прекращением
                            # брачных отношений и датой расторжения брака
                            if i.date_of_break_up < date_of_purchase:
                                marriage = i
                                after_break_up = True
                                link_name, law_link, law_text, npa = TEXTS['purchase_after_break_up']
                                link = Link(link_name, law_link, law_text, npa)
                                list_of_links.append(link)
                            # приобретение произошло до прекращения фактических отношений
                            else:
                                marriage = i
                        # факта прекращения брачных отношений не было
                        else:
                            marriage = i
                # если брак вообще не прекращался
                else:
                    marriage = i
                    # проверка на наличие факта прекращения брачных отношений
                    if i.date_of_break_up is not None:
                        # проверка на то, что приобретение произошло в период после фактического прекращения
                        # брачных отношений
                        if i.date_of_break_up < date_of_purchase:
                            marriage = i
                            after_break_up = True
                            link_name, law_link, law_text, npa = TEXTS['purchase_after_break_up']
                            link = Link(link_name, law_link, law_text, npa)
                            list_of_links.append(link)
                        # приобретение произошло до прекращения фактических отношений
                        else:
                            marriage = i
                    # факта прекращения брачных отношений не было
                    else:
                        marriage = i
        return marriage, after_break_up, list_of_links

    # если браков нет - возвращается default значение
        # TODO - можно отправлять форму № 2 и доп.вопросы, связанные с видом имущества
    return marriage, after_break_up, list_of_links

class Period_of_time():
    def __init__(self, start: datetime.date, end: datetime.date):
        self.start = start
        self.end = end

    def __str__(self):
        return f'Период с {self.start} по {self.end}'

    def __repr__(self):
        return f'Период с {self.start} по {self.end}'


def to_ownership(form_full: dict):
    name = form_full['name']
    type_of_property_form = form_full['type_of_property_form']
    type_of_property = form_full['type_of_property']
    obtaining_person = form_full['obtaining_person']
    date_of_purchase = form_full['date_of_purchase']
    price = form_full['price']
    list_of_links = form_full['list_of_links']
    marriage = form_full['marriage']
    after_break_up = form_full['after_break_up']
    dolya_chislitel = form_full['dolya_chislitel'][0]
    dolya_znamenatel = form_full['dolya_znamenatel'][0]


    # период с даты приобретения до окончания времен
    period_of_time = Period_of_time(date_of_purchase, datetime.date(2050, 1, 1))

    # указание долей, сособственников и т.п.
    owners = {}
    if marriage is not None:
        # определение супруга
        parties = list(marriage.parties.all())
        for i in parties:
            if i == obtaining_person:
                continue
            else:
                spouce = i
    # если указаны сособственники
    if 'coowners' in form_full:
        dolya_for_obtaining = f'{dolya_chislitel}/{dolya_znamenatel}'
        dolya_for_inie = f'{int(dolya_znamenatel) - int(dolya_chislitel)}/{dolya_znamenatel}'
        # если есть брак
        if marriage is not None:
            # если в браке after_break_up был True
            if after_break_up == True:
                owners[obtaining_person] = {'доля': dolya_for_obtaining,
                                            'совместные сособственники': None,
                                            'совместная доля': None}
                # для иных сособственников
                owners['Иные сособственники'] = {'доля': dolya_for_inie,
                                            'совместные сособственники': None,
                                            'совместная доля': None}
            # если after_break_up == False
            else:
                # описание для того, кто был указан приобретателем
                owners[obtaining_person] = {'доля': None,
                                            'совместные сособственники': spouce,
                                            'совместная доля': dolya_for_obtaining}
                # описание для супруга того, кто был указан приобретателем
                owners[spouce] = {'доля': None,
                                  'совместные сособственники': obtaining_person,
                                  'совместная доля': dolya_for_obtaining}
                # для иных сособственников
                owners[spouce] = {'доля': dolya_for_inie,
                                  'совместные сособственники': None,
                                  'совместная доля': None}
        # если брака нет
        else:
            owners[obtaining_person] = {'доля': dolya_for_obtaining,
                                        'совместные сособственники': None,
                                        'совместная доля': None}
            # для иных сособственников
            owners['Иные сособственники'] = {'доля': dolya_for_inie,
                                        'совместные сособственники': None,
                                        'совместная доля': None}

    # если сособственников нет
    else:
        # если есть брак
        if marriage is not None:
            # если в браке after_break_up был True
            if after_break_up == True:
                owners[obtaining_person] = {'доля': 1,
                                            'совместные сособственники': None,
                                            'совместная доля': None}
            # если after_break_up == False
            else:
                # описание для того, кто был указан приобретателем
                owners[obtaining_person] = {'доля': None,
                                            'совместные сособственники': spouce,
                                            'совместная доля': 1}
                # описание для супруга того, кто был указан приобретателем
                owners[spouce] = {'доля': None,
                                  'совместные сособственники': obtaining_person,
                                  'совместная доля': 1}
        # если брака нет
        else:
            owners[obtaining_person] = {'доля': 1,
                                        'совместные сособственники': None,
                                        'совместная доля': None}

    type_of_relationships = {'Собственность': owners}
    i_ownership = {period_of_time: type_of_relationships}
    ownership = {'ownership': i_ownership}
    return ownership
