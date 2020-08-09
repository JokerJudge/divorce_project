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
    :return:
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