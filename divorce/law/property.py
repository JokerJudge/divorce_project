from math import gcd # greatest common devisor
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

def clean_coowners(data: dict):
    '''
    Проверка на правильность заполнения поля с долями в праве
    :param data: словарь request.POST
    :return: словарь errors, если при заполнении были ошибки или None, если всё в порядке
    '''
    # валидация в форме № 1
    dolya_chislitel = data['dolya_chislitel']
    dolya_znamenatel = data['dolya_znamenatel']

    # здесь будет словарь ошибок по введенным долям
    errors = {}

    # если нет брака или указаны только id='coowners' (сособственники помимо супругов)
    if 'coowners' in data:
        errors.update(dolya_check(dolya_chislitel, dolya_znamenatel, 'сособственники'))

        # если происходит валидация формы № 1 - здесь будет выход
    if 'before_marriage_dolya_chislitel_wife' not in data:
        return errors

    # валидация в форме № 2
    before_marriage_dolya_chislitel_wife = data['before_marriage_dolya_chislitel_wife']
    before_marriage_dolya_znamenatel_wife = data['before_marriage_dolya_znamenatel_wife']
    before_marriage_dolya_chislitel_husband = data['before_marriage_dolya_chislitel_husband']
    before_marriage_dolya_znamenatel_husband = data['before_marriage_dolya_znamenatel_husband']

    common_dolya_chislitel = data['common_dolya_chislitel']
    common_dolya_znamenatel = data['common_dolya_znamenatel']

    private_dolya_chislitel_wife = data['private_dolya_chislitel_wife']
    private_dolya_znamenatel_wife = data['private_dolya_znamenatel_wife']
    private_dolya_chislitel_husband = data['private_dolya_chislitel_husband']
    private_dolya_znamenatel_husband = data['private_dolya_znamenatel_husband']

    present_dolya_chislitel_wife = data['present_dolya_chislitel_wife']
    present_dolya_znamenatel_wife = data['present_dolya_znamenatel_wife']
    present_dolya_chislitel_husband = data['present_dolya_chislitel_husband']
    present_dolya_znamenatel_husband = data['present_dolya_znamenatel_husband']

    inheritance_dolya_chislitel_wife = data['inheritance_dolya_chislitel_wife']
    inheritance_dolya_znamenatel_wife = data['inheritance_dolya_znamenatel_wife']
    inheritance_dolya_chislitel_husband = data['inheritance_dolya_chislitel_husband']
    inheritance_dolya_znamenatel_husband = data['inheritance_dolya_znamenatel_husband']


    # обрабатываем вариант, где выбрана "Покупка"
    if data['purchase_type'] == 'purchase_type_buy':
        print('Покупка')
        #обрабатываем вариант, если включен чекбокс "Часть/все деньги за имущество вносились до брака"
        if 'before_marriage' in data:
            # обрабатываем вариант, когда выбрано, что деньги до брака вносились только женой в части
            if 'before_marriage_wife' in data and 'before_marriage_husband' not in data:
                # если выбран вариант "в части"
                if data['before_marriage_wife_amount'] == 'before_marriage_wife_amount_dolya':
                    errors.update(dolya_check(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife, 'доля жены до брака'))
                    # проверяем вариант, когда до брака только женой, а остаток полностью за счет общий средств
                    if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' not in data:
                        # Если было указано, что остаток полностью вносился за счет общего имущества
                        # ostatok - было ли отмечено поле "полностью"
                        if data['common_amount'] == 'common_amount_all':
                            errors.update(dolya_math(before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                                     ostatok=True))
                        # Если была выбрана доля общего имущества
                        if data['common_amount'] == 'common_amount_dolya':
                            errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                            errors.update(dolya_math(before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                                     common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))

                    # проверяем вариант, когда до брака только женой, а остаток полностью за счет средств жены
                    if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' not in data:
                        # Если было указано, что остаток полностью вносился за счет средств жены
                        # ostatok - было ли отмечено поле "полностью"
                        if data['private_wife_amount'] == 'private_wife_amount_all':
                            errors.update(dolya_math(before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                                     ostatok=True))
                        # Если была выбрана "часть средств жены"
                        if data['private_wife_amount'] == 'private_wife_amount_dolya':
                            errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife, 'личные средства жены'))
                            errors.update(dolya_math(before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                                     private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife)))

                    # проверяем вариант, когда до брака только женой, а остаток полностью за счет средств мужа
                    if 'common_dolya' not in data and 'private_wife' not in data and 'private_husband' in data:
                        # Если было указано, что остаток полностью вносился за счет средств мужа
                        # ostatok - было ли отмечено поле "полностью"
                        if data['private_husband_amount'] == 'private_husband_amount_all':
                            errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                                     ostatok=True))
                        # Если была выбрана "часть средств мужа"
                        if data['private_husband_amount'] == 'private_husband_amount_dolya':
                            errors.update(
                                dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                            'личные средства мужа'))
                            errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                                     private_dolya_husband=(private_dolya_chislitel_husband,
                                                                         private_dolya_znamenatel_husband)))

                    # проверяем вариант, когда до брака только женой, а остаток за счет общих средств и личных средств жены
                    if 'common_dolya' in data and 'private_wife' in data and 'private_husband' not in data:
                        errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                                  'личные средства жены'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_wife=(private_dolya_chislitel_wife,
                                                   private_dolya_znamenatel_wife)))

                    # проверяем вариант, когда до брака только женой, а остаток за счет общих средств и личных средств мужа
                    if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' in data:
                        errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                                  'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                private_dolya_znamenatel_husband)))

                    # проверяем вариант, когда до брака только женой, а остаток за счет личных средств жены и личных средств мужа
                    if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' in data:
                        errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife, 'личные средства жены'))
                        errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                                  'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                   private_dolya_znamenatel_husband)))


            # обрабатываем вариант, когда выбрано, что деньги до брака вносились только мужем в части
            if 'before_marriage_wife' not in data and 'before_marriage_husband' in data:
                # если выбран вариант "в части"
                if data['before_marriage_husband_amount'] == 'before_marriage_husband_amount_dolya':
                    errors.update(dolya_check(before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband, 'доля мужа до брака'))
                    # проверяем вариант, когда до брака только мужем, а остаток полностью за счет общих средств
                    if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' not in data:
                        # Если было указано, что остаток полностью вносился за счет общего имущества
                        # ostatok - было ли отмечено поле "полностью"
                        if data['common_amount'] == 'common_amount_all':
                            errors.update(dolya_math(before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                                                     ostatok=True))
                        # Если была выбрана доля общего имущества
                        if data['common_amount'] == 'common_amount_dolya':
                            errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                            errors.update(dolya_math(before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                                                     common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))

                    # проверяем вариант, когда до брака только мужем, а остаток полностью за счет средств жены
                    if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' not in data:
                        # Если было указано, что остаток полностью вносился за счет средств жены
                        # ostatok - было ли отмечено поле "полностью"
                        if data['private_wife_amount'] == 'private_wife_amount_all':
                            errors.update(dolya_math(before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                                                     ostatok=True))
                        # Если была выбрана "часть средств жены"
                        if data['private_wife_amount'] == 'private_wife_amount_dolya':
                            errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife, 'личные средства жены'))
                            errors.update(dolya_math(before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                                                     private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife)))

                    # проверяем вариант, когда до брака только женой, а остаток полностью за счет средств мужа
                    if 'common_dolya' not in data and 'private_wife' not in data and 'private_husband' in data:
                        # Если было указано, что остаток полностью вносился за счет средств мужа
                        # ostatok - было ли отмечено поле "полностью"
                        if data['private_husband_amount'] == 'private_husband_amount_all':
                            errors.update(dolya_math(before_marriage_dolya_husband=(
                            before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                                                     ostatok=True))
                        # Если была выбрана "часть средств мужа"
                        if data['private_husband_amount'] == 'private_husband_amount_dolya':
                            errors.update(
                                dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                            'личные средства мужа'))
                            errors.update(dolya_math(before_marriage_dolya_husband=(
                            before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                                                     private_dolya_husband=(private_dolya_chislitel_husband,
                                                                         private_dolya_znamenatel_husband)))

                    # проверяем вариант, когда до брака только мужем, а остаток за счет общих средств и личных средств жены
                    if 'common_dolya' in data and 'private_wife' in data and 'private_husband' not in data:
                        errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                                  'личные средства жены'))
                        errors.update(dolya_math(before_marriage_dolya_husband=(
                            before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_wife=(private_dolya_chislitel_wife,
                                                   private_dolya_znamenatel_wife)))

                    # проверяем вариант, когда до брака только мужем, а остаток за счет общих средств и личных средств мужа
                    if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' in data:
                        errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                                  'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_husband=(
                            before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                private_dolya_znamenatel_husband)))

                    # проверяем вариант, когда до брака только мужем, а остаток за счет личных средств жены и личных средств мужа
                    if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' in data:
                        errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife, 'личные средства жены'))
                        errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                                  'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_husband=(
                            before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                   private_dolya_znamenatel_husband)))

            # обрабатываем вариант, когда выбрано, что деньги вносили обоими будущими супругами
            if 'before_marriage_wife' in data and 'before_marriage_husband' in data:
                errors.update(dolya_check(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife,'доля жены до брака'))
                errors.update(dolya_check(before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband,'доля мужа до брака'))

                # если выбран вариант "полностью"
                # проверяем вариант, когда до брака обоими будущими супругами, а остаток полностью за счет общих средств
                if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' not in data:
                    # Если было указано, что остаток полностью вносился за счет общего имущества
                    # ostatok - было ли отмечено поле "полностью"
                    if data['common_amount'] == 'common_amount_all':
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife,
                            before_marriage_dolya_znamenatel_wife),
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            ostatok=True))
                    # Если была выбрана доля общего имущества
                    if data['common_amount'] == 'common_amount_dolya':
                        errors.update(
                            dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife,
                            before_marriage_dolya_znamenatel_wife),
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            common_dolya=(
                                common_dolya_chislitel, common_dolya_znamenatel)))

                # проверяем вариант, когда до брака обоими будущими супругами, а остаток полностью за счет средств жены
                if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' not in data:
                    # Если было указано, что остаток полностью вносился за счет средств жены
                    # ostatok - было ли отмечено поле "полностью"
                    if data['private_wife_amount'] == 'private_wife_amount_all':
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                        before_marriage_dolya_chislitel_wife,
                        before_marriage_dolya_znamenatel_wife),
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                                                 ostatok=True))
                    # Если была выбрана "часть средств жены"
                    if data['private_wife_amount'] == 'private_wife_amount_dolya':
                        errors.update(
                            dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                        'личные средства жены'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                        before_marriage_dolya_chislitel_wife,
                        before_marriage_dolya_znamenatel_wife),
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                                                 private_dolya_wife=(private_dolya_chislitel_wife,
                                                                     private_dolya_znamenatel_wife)))

                # проверяем вариант, когда до брака обоими будущими супругами, а остаток полностью за счет средств мужа
                if 'common_dolya' not in data and 'private_wife' not in data and 'private_husband' in data:
                    # Если было указано, что остаток полностью вносился за счет средств мужа
                    # ostatok - было ли отмечено поле "полностью"
                    if data['private_husband_amount'] == 'private_husband_amount_all':
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife,
                            before_marriage_dolya_znamenatel_wife),
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            ostatok=True))
                    # Если была выбрана "часть средств мужа"
                    if data['private_husband_amount'] == 'private_husband_amount_dolya':
                        errors.update(
                            dolya_check(private_dolya_chislitel_husband,
                                        private_dolya_znamenatel_husband,
                                        'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife,
                            before_marriage_dolya_znamenatel_wife),
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                   private_dolya_znamenatel_husband)))

                # проверяем вариант, когда до брака обоими будущими супругами, а остаток за счет общих средств и личных средств жены
                if 'common_dolya' in data and 'private_wife' in data and 'private_husband' not in data:
                    errors.update(
                        dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                    errors.update(
                        dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                    'личные средства жены'))
                    errors.update(dolya_math(before_marriage_dolya_wife=(
                        before_marriage_dolya_chislitel_wife,
                        before_marriage_dolya_znamenatel_wife),
                        before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                       before_marriage_dolya_znamenatel_husband),
                        common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                        private_dolya_wife=(private_dolya_chislitel_wife,
                                            private_dolya_znamenatel_wife)))

                # проверяем вариант, когда до брака обоими будущими супругами, а остаток за счет общих средств и личных средств мужа
                if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' in data:
                    errors.update(
                        dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                    errors.update(
                        dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                    'личные средства мужа'))
                    errors.update(dolya_math(before_marriage_dolya_wife=(
                        before_marriage_dolya_chislitel_wife,
                        before_marriage_dolya_znamenatel_wife),
                        before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                       before_marriage_dolya_znamenatel_husband),
                        common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                        private_dolya_husband=(private_dolya_chislitel_husband,
                                               private_dolya_znamenatel_husband)))

                # проверяем вариант, когда до брака только мужем, а остаток за счет личных средств жены и личных средств мужа
                if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' in data:
                    errors.update(
                        dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                    'личные средства жены'))
                    errors.update(
                        dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                    'личные средства мужа'))
                    errors.update(dolya_math(before_marriage_dolya_wife=(
                        before_marriage_dolya_chislitel_wife,
                        before_marriage_dolya_znamenatel_wife),
                        before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                       before_marriage_dolya_znamenatel_husband),
                        private_dolya_wife=(
                        private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        private_dolya_husband=(private_dolya_chislitel_husband,
                                               private_dolya_znamenatel_husband)))

    return errors

def dolya_check(chislitel, znamenatel, where):
    '''
    Функция, валидирующая правильность ввода числителя и знаменателя без операций между разными полями
    :param chislitel: числитель
    :param znamenatel: знаменатель
    :param where: где произошла ошибка
    :return: словарь с ошибками, если они там есть. Если нет - пустой словарь
    '''
    errors = {}
    if not chislitel or not znamenatel or int(chislitel) <= 0 or int(znamenatel) <= 0:
        errors[f'Доля в праве в поле "{where}" указана неверно'] = f'{chislitel}/{znamenatel}'

    if chislitel and znamenatel:
        if int(chislitel) >= int(znamenatel):
            errors[f'Числитель в поле "{where}" не может быть больше или равен знаменателю'] = f'{chislitel}/{znamenatel}'
    return errors

def dolya_math(before_marriage_dolya_wife=('', ''),
               before_marriage_dolya_husband=('', ''),
               common_dolya=('', ''),
               private_dolya_wife=('', ''),
               private_dolya_husband=('',''),
               present_dolya_wife=('', ''),
               present_dolya_husband=('', ''),
               inheritance_dolya_wife=('', ''),
               inheritance_dolya_husband=('',''),
               ostatok=False):

    dolya_dict_temp = locals().copy()
    print(dolya_dict_temp)
    del dolya_dict_temp['ostatok']
    dolya_dict = dolya_dict_temp.copy()
    errors = {}
    list_of_chislitels = []
    list_of_znamenatels = []

    for k, v in dolya_dict_temp.items():
        if v[1] != '':
            list_of_znamenatels.append(int(v[1]))
            dolya_dict[f'{k}'] = (int(v[0]), int(v[1]))
        else:
            del dolya_dict[f'{k}']

    print(list_of_chislitels)
    print(list_of_znamenatels)
    print(dolya_dict)

    znam = list_of_znamenatels[0]

    # если одно поле заполнено
    if len(list_of_znamenatels) == 1:
        flag = 'Иные сособственники'
        temp_chislitel = 1
        for k, v in dolya_dict.items():
            temp_chislitel = dolya_dict[f'{k}'][0]
            # Если было помечено поле "Полностью"
            if ostatok == True:
                flag = 'Остаток'
        dolya_dict[flag] = (znam - temp_chislitel, znam)
    # TODO - предусмотреть вариант, если "полностью" будет отмечен
    else:

        for i in range(len(list_of_znamenatels)):
            # находим общий знаменатель всех знаменателей, которые ввел пользователь
            if i == 0:
                temp_znam = list_of_znamenatels[i]
                print('temp_znam')
                print(temp_znam)
            else:
                #znam = (list_of_znamenatels[i] * list_of_znamenatels[i-1] // gcd(list_of_znamenatels[i], list_of_znamenatels[i-1]))
                znam = (list_of_znamenatels[i] * temp_znam // gcd(list_of_znamenatels[i], temp_znam))
                temp_znam = znam
            print(znam)

        # преобразовываем всё, переданное в функцию, в дроби с общим знаменателем
        list_for_display = []
        summ = 0

        for k, v in dolya_dict.items():
            if v[1] == znam:
                pass
            elif v[1] != znam:
                temp = znam // v[1]
                dolya_dict[f'{k}'] = ((v[0] * temp), znam)
            summ += dolya_dict[f'{k}'][0]
            list_for_display.append(v[0])
            list_for_display.append(v[1])
        if summ > znam:
            errors['Сумма всех долей оказалась больше 100%, такого быть не может'] = f'{summ} / {znam}'
        elif summ < znam:
            dolya_dict['Иные сособственники'] = (znam - summ, znam)


    print(dolya_dict)
    if True:
        return errors
    # TODO - нужно вернуть значение dolya_dict и errors, если эта функция будет использоваться при добавлении долей в БД
    #return errors, dolya_dict
