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
    list_of_links.append(to_link('marriage_periods'))

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
                                list_of_links.append(to_link('purchase_after_break_up'))
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
                            list_of_links.append(to_link('purchase_after_break_up'))
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

    # инициализация переменных из формы № 2 при отсутствии браков
    if 'dolya_chislitel' in form_full:
        dolya_chislitel = form_full['dolya_chislitel'][0]
        dolya_znamenatel = form_full['dolya_znamenatel'][0]

    # инициализация переменных из формы № 2 при наличии брака
    if 'before_marriage_dolya_chislitel_wife' in form_full:

        before_marriage_dolya_chislitel_wife = form_full['before_marriage_dolya_chislitel_wife'][0]
        before_marriage_dolya_znamenatel_wife = form_full['before_marriage_dolya_znamenatel_wife'][0]
        before_marriage_dolya_chislitel_husband = form_full['before_marriage_dolya_chislitel_husband'][0]
        before_marriage_dolya_znamenatel_husband = form_full['before_marriage_dolya_znamenatel_husband'][0]

        common_dolya_chislitel = form_full['common_dolya_chislitel'][0]
        common_dolya_znamenatel = form_full['common_dolya_znamenatel'][0]

        private_dolya_chislitel_wife = form_full['private_dolya_chislitel_wife'][0]
        private_dolya_znamenatel_wife = form_full['private_dolya_znamenatel_wife'][0]
        private_dolya_chislitel_husband = form_full['private_dolya_chislitel_husband'][0]
        private_dolya_znamenatel_husband = form_full['private_dolya_znamenatel_husband'][0]

        present_dolya_chislitel_wife = form_full['present_dolya_chislitel_wife'][0]
        present_dolya_znamenatel_wife = form_full['present_dolya_znamenatel_wife'][0]
        present_dolya_chislitel_husband = form_full['present_dolya_chislitel_husband'][0]
        present_dolya_znamenatel_husband = form_full['present_dolya_znamenatel_husband'][0]

        inheritance_dolya_chislitel_wife = form_full['inheritance_dolya_chislitel_wife'][0]
        inheritance_dolya_znamenatel_wife = form_full['inheritance_dolya_znamenatel_wife'][0]
        inheritance_dolya_chislitel_husband = form_full['inheritance_dolya_chislitel_husband'][0]
        inheritance_dolya_znamenatel_husband = form_full['inheritance_dolya_znamenatel_husband'][0]


    # период с даты приобретения до окончания времен
    period_of_time = Period_of_time(date_of_purchase, datetime.date(2050, 1, 1))


    owners = {}
    # описываем вариант, когда брака нет
    if marriage == None:
        # когда есть сособственники
        if 'coowners' in form_full:

            dolya_for_obtaining = f'{dolya_chislitel}/{dolya_znamenatel}'
            dolya_for_inie = f'{int(dolya_znamenatel) - int(dolya_chislitel)}/{dolya_znamenatel}'

            owners[obtaining_person] = {'доля': dolya_for_obtaining,
                                        'совместные сособственники': None,
                                        'совместная доля': None}
            # для иных сособственников
            owners['Иные сособственники'] = {'доля': dolya_for_inie,
                                             'совместные сособственники': None,
                                             'совместная доля': None}
            list_of_links.append(to_link('common_property_dolevaya'))

        # сособственников нет
        else:
            owners[obtaining_person] = {'доля': 1,
                                        'совместные сособственники': None,
                                        'совместная доля': None}

            list_of_links.append(to_link('individual_property'))


    # когда брак есть
    if marriage is not None:
        # определение супруга
        parties = list(marriage.parties.all())
        for i in parties:
            if i == obtaining_person:
                if obtaining_person.sex == 'М':
                    husband = obtaining_person
                else:
                    wife = obtaining_person
            else:
                spouce = i
                if spouce.sex == 'М':
                    husband = spouce
                else:
                    wife = spouce

        # если выбрана "Покупка"
        if form_full['purchase_type'] == ['purchase_type_buy']:
            # обрабатываем вариант, если включен чекбокс "Часть/все деньги за имущество вносились до брака"
            # TODO - сделать без before_marriage
            if 'before_marriage' in form_full:
                # обрабатываем вариант, когда выбрано, что деньги до брака вносились только женой
                if 'before_marriage_wife' in form_full and 'before_marriage_husband' not in form_full:
                    # если выбран вариант "полностью"
                    if form_full['before_marriage_wife_amount'] == ['before_marriage_wife_amount_all']:
                        owners[wife] = {'доля': 1,
                                        'совместные сособственники': None,
                                        'совместная доля': None}

                        list_of_links.append(to_link('individual_property'))
                        list_of_links.append(to_link('purchase_before_marriage'))

                    # если выбран вариант "в части"
                    if form_full['before_marriage_wife_amount'] == ['before_marriage_wife_amount_dolya']:
                        # проверяем вариант, когда до брака только женой, а остаток полностью за счет общий средств
                        if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' not in form_full:
                            # Если было указано, что остаток полностью вносился за счет общего имущества
                            # ostatok - было ли отмечено поле "полностью"
                            if form_full['common_amount'] == ['common_amount_all']:
                                dolya_dict = dolya_math(before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                                       before_marriage_dolya_znamenatel_wife),
                                                        ostatok=True,
                                                        flag_ownership='ownership')
                                print(dolya_dict)

                                owners[wife] = {'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                                'совместные сособственники': husband,
                                                'совместная доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}'}
                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                                owners[husband] = {'доля': None,
                                                   'совместные сособственники': wife,
                                                   'совместная доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}'}
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                            # Если была выбрана доля общего имущества
                            if form_full['common_amount'] == ['common_amount_dolya']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                                before_marriage_dolya_znamenatel_wife),
                                    common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': husband,
                                    'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                                owners[husband] = {'доля': None,
                                                   'совместные сособственники': wife,
                                                   'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                                if 'Иные сособственники' in dolya_dict:
                                    owners['Иные сособственники'] = {'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                                       'совместные сособственники': None,
                                                       'совместная доля': None}
                                    list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только женой, а остаток полностью за счет средств жены
                        if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                            # Если было указано, что остаток полностью вносился за счет средств жены
                            # ostatok - было ли отмечено поле "полностью"
                            if form_full['private_wife_amount'] == ['private_wife_amount_all']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                                before_marriage_dolya_znamenatel_wife),
                                    ostatok=True,
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[wife] = {
                                    'доля': 1,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                            # Если была выбрана "часть средств жены"
                            if form_full['private_wife_amount'] == ['private_wife_amount_dolya']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                                before_marriage_dolya_znamenatel_wife),
                                    private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                    flag_ownership='ownership')

                                print(dolya_dict)
                                # необходимо сложить дроби личного имущества до брака и во время брака
                                dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["private_dolya_wife"][0]
                                if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_wife"][1]:
                                    dolya_wife = 1
                                else:
                                    dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_wife"][1]}'

                                owners[wife] = {
                                    'доля': dolya_wife,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('purchase_marriage_private_money'))
                                list_of_links.append(to_link('common_property_dolevaya'))

                                if 'Иные сособственники' in dolya_dict:
                                    owners['Иные сособственники'] = {
                                        'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                        'совместные сособственники': None,
                                        'совместная доля': None}
                                    list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только женой, а остаток полностью за счет средств мужа
                        if 'common_dolya' not in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                            # Если было указано, что остаток полностью вносился за счет средств мужа
                            # ostatok - было ли отмечено поле "полностью"
                            if form_full['private_husband_amount'] == ['private_husband_amount_all']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                                before_marriage_dolya_znamenatel_wife),
                                    ostatok=True,
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[husband] = {
                                    'доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                            # Если была выбрана "часть средств мужа"
                            if form_full['private_husband_amount'] == ['private_husband_amount_dolya']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                                before_marriage_dolya_znamenatel_wife),
                                    private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[husband] = {
                                    'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                                if 'Иные сособственники' in dolya_dict:
                                    owners['Иные сособственники'] = {
                                        'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                        'совместные сособственники': None,
                                        'совместная доля': None}
                                    list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только женой, а остаток за счет общих средств и личных средств жены
                        if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                            before_marriage_dolya_znamenatel_wife),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                private_dolya_wife=(
                                private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                flag_ownership='ownership')

                            # необходимо сложить дроби личного имущества до брака и во время брака
                            dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["private_dolya_wife"][0]
                            if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_wife"][1]:
                                dolya_wife = 1
                            else:
                                dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_wife"][1]}'

                            owners[wife] = {
                                'доля': dolya_wife,
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            owners[husband] = {
                                'доля': None,
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))
                        # проверяем вариант, когда до брака только женой, а остаток за счет общих средств и личных средств мужа
                        if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                            before_marriage_dolya_znamenatel_wife),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            owners[wife] = {
                                'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            owners[husband] = {
                                'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только женой, а остаток за счет личных средств жены и личных средств мужа
                        if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                            before_marriage_dolya_znamenatel_wife),
                                private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            # необходимо сложить дроби личного имущества до брака и во время брака
                            dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["private_dolya_wife"][0]
                            if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_wife"][1]:
                                dolya_wife = 1
                            else:
                                dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_wife"][1]}'

                            owners[wife] = {
                                'доля': dolya_wife,
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_dolevaya'))

                            owners[husband] = {
                                'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_dolevaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только женой, а остаток за счет общих средств, личных средств жены и личных средств мужа
                        if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife,
                                                            before_marriage_dolya_znamenatel_wife),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            # необходимо сложить дроби личного имущества до брака и во время брака
                            dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["private_dolya_wife"][0]
                            if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_wife"][1]:
                                dolya_wife = 1
                            else:
                                dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_wife"][1]}'

                            owners[wife] = {
                                'доля': dolya_wife,
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            owners[husband] = {
                                'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                # обрабатываем вариант, когда выбрано, что деньги до брака вносились только мужем
                if 'before_marriage_wife' not in form_full and 'before_marriage_husband' in form_full:
                    # если выбран вариант "полностью"
                    if form_full['before_marriage_husband_amount'] == ['before_marriage_husband_amount_all']:
                        owners[husband] = {'доля': 1,
                                        'совместные сособственники': None,
                                        'совместная доля': None}

                        list_of_links.append(to_link('individual_property'))
                        list_of_links.append(to_link('purchase_before_marriage'))

                    # если выбран вариант "в части"
                    if form_full['before_marriage_husband_amount'] == ['before_marriage_husband_amount_dolya']:
                        # проверяем вариант, когда до брака только мужем, а остаток полностью за счет общих средств
                        if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' not in form_full:
                            # Если было указано, что остаток полностью вносился за счет общего имущества
                            # ostatok - было ли отмечено поле "полностью"
                            if form_full['common_amount'] == ['common_amount_all']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                                before_marriage_dolya_znamenatel_husband),
                                    ostatok=True,
                                    flag_ownership='ownership')
                                print(dolya_dict)

                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': wife,
                                    'совместная доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}'}
                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                                owners[wife] = {'доля': None,
                                                'совместные сособственники': husband,
                                                'совместная доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}'}
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                            # Если была выбрана доля общего имущества
                            if form_full['common_amount'] == ['common_amount_dolya']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                                before_marriage_dolya_znamenatel_husband),
                                    common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': wife,
                                    'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                                owners[wife] = {'доля': None,
                                                'совместные сособственники': husband,
                                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                                if 'Иные сособственники' in dolya_dict:
                                    owners['Иные сособственники'] = {
                                        'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                        'совместные сособственники': None,
                                        'совместная доля': None}
                                    list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только мужем, а остаток полностью за счет средств жены
                        if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                            # Если было указано, что остаток полностью вносился за счет средств жены
                            # ostatok - было ли отмечено поле "полностью"
                            if form_full['private_wife_amount'] == ['private_wife_amount_all']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                                before_marriage_dolya_znamenatel_husband),
                                    ostatok=True,
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                            # Если была выбрана "часть средств жены"
                            if form_full['private_wife_amount'] == ['private_wife_amount_dolya']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                                before_marriage_dolya_znamenatel_husband),
                                    private_dolya_wife=(
                                    private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                    flag_ownership='ownership')

                                print(dolya_dict)

                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_marriage_private_money'))
                                list_of_links.append(to_link('common_property_dolevaya'))

                                if 'Иные сособственники' in dolya_dict:
                                    owners['Иные сособственники'] = {
                                        'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                        'совместные сособственники': None,
                                        'совместная доля': None}
                                    list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только мужем, а остаток полностью за счет средств мужа
                        if 'common_dolya' not in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                            # Если было указано, что остаток полностью вносился за счет средств мужа
                            # ostatok - было ли отмечено поле "полностью"
                            if form_full['private_husband_amount'] == ['private_husband_amount_all']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                                before_marriage_dolya_znamenatel_husband),
                                    ostatok=True,
                                    flag_ownership='ownership')

                                owners[husband] = {'доля': 1,
                                                   'совместные сособственники': None,
                                                   'совместная доля': None}

                                list_of_links.append(to_link('individual_property'))
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                            # Если была выбрана "часть средств мужа"
                            if form_full['private_husband_amount'] == ['private_husband_amount_dolya']:
                                dolya_dict = dolya_math(
                                    before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                                before_marriage_dolya_znamenatel_husband),
                                    private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                    flag_ownership='ownership')

                                # необходимо сложить дроби личного имущества до брака и во время брака
                                dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + dolya_dict["private_dolya_husband"][0]
                                if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                    dolya_husband = 1
                                else:
                                    dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                                owners[husband] = {
                                    'доля': dolya_husband,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                                if 'Иные сособственники' in dolya_dict:
                                    owners['Иные сособственники'] = {
                                        'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                        'совместные сособственники': None,
                                        'совместная доля': None}
                                    list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только мужем, а остаток за счет общих средств и личных средств жены
                        if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                            before_marriage_dolya_znamenatel_husband),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                private_dolya_wife=(
                                    private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                flag_ownership='ownership')

                            owners[husband] = {
                                'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            owners[wife] = {
                                'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_marriage_private_money'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только мужем, а остаток за счет общих средств и личных средств мужа
                        if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                            before_marriage_dolya_znamenatel_husband),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            # необходимо сложить дроби личного имущества до брака и во время брака
                            dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + dolya_dict["private_dolya_husband"][0]
                            if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                dolya_husband = 1
                            else:
                                dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                            owners[husband] = {
                                'доля': dolya_husband,
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            owners[wife] = {
                                'доля': None,
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только мужем, а остаток за счет личных средств жены и личных средств мужа
                        if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                            before_marriage_dolya_znamenatel_husband),
                                private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            # необходимо сложить дроби личного имущества до брака и во время брака
                            dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + \
                                                      dolya_dict["private_dolya_husband"][0]
                            if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                dolya_husband = 1
                            else:
                                dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                            owners[husband] = {
                                'доля': dolya_husband,
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_dolevaya'))

                            owners[wife] = {
                                'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_marriage_private_money'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                        # проверяем вариант, когда до брака только мужем, а остаток за счет общих средств, личных средств жены и личных средств мужа
                        if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                            before_marriage_dolya_znamenatel_husband),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                private_dolya_husband=(
                                    private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            # необходимо сложить дроби личного имущества до брака и во время брака
                            dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + \
                                                      dolya_dict["private_dolya_husband"][0]
                            if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                dolya_husband = 1
                            else:
                                dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                            owners[husband] = {
                                'доля': dolya_husband,
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            owners[wife] = {
                                'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_marriage_private_money'))
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                # обрабатываем вариант, когда выбрано, что деньги вносились обоими будущими супругами
                if 'before_marriage_wife' in form_full and 'before_marriage_husband' in form_full:
                    # если выбран вариант "полностью"
                    # проверяем вариант, когда до брака обоими будущими супругами, а остаток полностью за счет общих средств
                    if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' not in form_full:
                        # Если было указано, что остаток полностью вносился за счет общего имущества
                        # ostatok - было ли отмечено поле "полностью"
                        if form_full['common_amount'] == ['common_amount_all']:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                               before_marriage_dolya_znamenatel_husband),
                                before_marriage_dolya_wife=(before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                ostatok=True,
                                flag_ownership='ownership')

                            # если введены доли, которые в сумме не дают 1 (появляется совместная собственность)
                            if 'Остаток' in dolya_dict:
                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': wife,
                                    'совместная доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}'}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': husband,
                                    'совместная доля': f'{dolya_dict["Остаток"][0]}/{dolya_dict["Остаток"][1]}'}
                                list_of_links.append(to_link('common_property_sovmestnaya'))

                            else:
                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}

                        # Если была выбрана доля общего имущества
                        if form_full['common_amount'] == ['common_amount_dolya']:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                               before_marriage_dolya_znamenatel_husband),
                                before_marriage_dolya_wife=(
                                before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                                flag_ownership='ownership')

                            owners[husband] = {
                                'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                'совместные сособственники': wife,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('purchase_before_marriage'))

                            owners[wife] = {
                                'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                'совместные сособственники': husband,
                                'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                            list_of_links.append(to_link('common_property_sovmestnaya'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                    # проверяем вариант, когда до брака обоими будущими супругами, а остаток полностью за счет средств жены
                    if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                        # Если было указано, что остаток полностью вносился за счет средств жены
                        # ostatok - было ли отмечено поле "полностью"
                        if form_full['private_wife_amount'] == ['private_wife_amount_all']:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                               before_marriage_dolya_znamenatel_husband),
                                before_marriage_dolya_wife=(
                                before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                ostatok=True,
                                flag_ownership='ownership')

                            # если введены доли, которые в сумме не дают 1 (необходимо добавить остаток в долю жены)
                            if 'Остаток' in dolya_dict:
                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                # необходимо сложить дроби личного имущества до брака и во время брака
                                dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["Остаток"][0]
                                if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                    dolya_wife = 1
                                else:
                                    dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                                owners[wife] = {
                                    'доля': dolya_wife,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                            else:
                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}

                        # Если была выбрана "часть средств жены"
                        if form_full['private_wife_amount'] == ['private_wife_amount_dolya']:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                               before_marriage_dolya_znamenatel_husband),
                                before_marriage_dolya_wife=(
                                    before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                                flag_ownership='ownership')

                            owners[husband] = {
                                'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_before_marriage'))

                            dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["private_dolya_wife"][0]
                            if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                dolya_wife = 1
                            else:
                                dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                            owners[wife] = {
                                'доля': dolya_wife,
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_marriage_private_money'))

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                    # проверяем вариант, когда до брака обоими будущими супругами, а остаток полностью за счет средств мужа
                    if 'common_dolya' not in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                        # Если было указано, что остаток полностью вносился за счет средств мужа
                        # ostatok - было ли отмечено поле "полностью"
                        if form_full['private_husband_amount'] == ['private_husband_amount_all']:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                               before_marriage_dolya_znamenatel_husband),
                                before_marriage_dolya_wife=(
                                    before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                ostatok=True,
                                flag_ownership='ownership')

                            # если введены доли, которые в сумме не дают 1 (необходимо добавить остаток в долю мужа)
                            if 'Остаток' in dolya_dict:
                                # необходимо сложить дроби личного имущества до брака и во время брака
                                dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + dolya_dict["Остаток"][0]
                                if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                    dolya_husband = 1
                                else:
                                    dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                                owners[husband] = {
                                    'доля': dolya_husband,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))
                                list_of_links.append(to_link('purchase_marriage_private_money'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}

                            else:
                                owners[husband] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('purchase_before_marriage'))

                                owners[wife] = {
                                    'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}

                        # Если была выбрана "часть средств мужа"
                        if form_full['private_husband_amount'] == ['private_husband_amount_dolya']:
                            dolya_dict = dolya_math(
                                before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                               before_marriage_dolya_znamenatel_husband),
                                before_marriage_dolya_wife=(
                                    before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                                private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                                flag_ownership='ownership')

                            dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + dolya_dict["private_dolya_husband"][0]
                            if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                                dolya_husband = 1
                            else:
                                dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                            owners[husband] = {
                                'доля': dolya_husband,
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('purchase_before_marriage'))
                            list_of_links.append(to_link('purchase_marriage_private_money'))

                            owners[wife] = {
                                'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}

                            if 'Иные сособственники' in dolya_dict:
                                owners['Иные сособственники'] = {
                                    'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                                list_of_links.append(to_link('common_property_dolevaya'))

                    # проверяем вариант, когда до брака обоими будущими супругами, а остаток за счет общих средств и личных средств жены
                    if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                        dolya_dict = dolya_math(
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            before_marriage_dolya_wife=(
                                before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            flag_ownership='ownership')

                        owners[husband] = {
                            'доля': f'{dolya_dict["before_marriage_dolya_husband"][0]}/{dolya_dict["before_marriage_dolya_husband"][1]}',
                            'совместные сособственники': wife,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                        list_of_links.append(to_link('purchase_before_marriage'))

                        #неообходимо сложить личные доли жены в имуществе до брака и после брака
                        dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + dolya_dict["private_dolya_wife"][0]
                        if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                            dolya_wife = 1
                        else:
                            dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                        owners[wife] = {
                            'доля': dolya_wife,
                            'совместные сособственники': husband,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                        list_of_links.append(to_link('purchase_marriage_private_money'))
                        list_of_links.append(to_link('common_property_sovmestnaya'))

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('common_property_dolevaya'))

                    # проверяем вариант, когда до брака обоими будущими супругами, а остаток за счет общих средств и личных средств мужа
                    if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                        dolya_dict = dolya_math(
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            before_marriage_dolya_wife=(
                                before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                            flag_ownership='ownership')

                        # неообходимо сложить личные доли мужа в имуществе до брака и после брака
                        dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + dolya_dict["private_dolya_husband"][0]
                        if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                            dolya_husband = 1
                        else:
                            dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                        owners[husband] = {
                            'доля': dolya_husband,
                            'совместные сособственники': wife,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                        list_of_links.append(to_link('purchase_before_marriage'))
                        list_of_links.append(to_link('purchase_marriage_private_money'))

                        owners[wife] = {
                            'доля': f'{dolya_dict["before_marriage_dolya_wife"][0]}/{dolya_dict["before_marriage_dolya_wife"][1]}',
                            'совместные сособственники': husband,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                        list_of_links.append(to_link('common_property_sovmestnaya'))

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('common_property_dolevaya'))

                    # проверяем вариант, когда до брака обоими будущими супругами, а остаток за счет личных средств жены и личных средств мужа
                    if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                        dolya_dict = dolya_math(
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            before_marriage_dolya_wife=(
                                before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                            flag_ownership='ownership')

                        # неообходимо сложить личные доли мужа в имуществе до брака и после брака
                        dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + \
                                                  dolya_dict["private_dolya_husband"][0]
                        if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                            dolya_husband = 1
                        else:
                            dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                        owners[husband] = {
                            'доля': dolya_husband,
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('purchase_before_marriage'))
                        list_of_links.append(to_link('purchase_marriage_private_money'))

                        # неообходимо сложить личные доли жены в имуществе до брака и после брака
                        dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + \
                                                  dolya_dict["private_dolya_wife"][0]
                        if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_wife"][1]:
                            dolya_wife = 1
                        else:
                            dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                        owners[wife] = {
                            'доля': dolya_wife,
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}

                    # проверяем вариант, когда до брака только обоими будущими супругами, а остаток за счет общих средств, личных средств жены и личных средств мужа
                    if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                        dolya_dict = dolya_math(
                            before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                           before_marriage_dolya_znamenatel_husband),
                            before_marriage_dolya_wife=(
                                before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                            flag_ownership='ownership')

                        # неообходимо сложить личные доли мужа в имуществе до брака и после брака
                        dolya_husband_chislitel = dolya_dict["before_marriage_dolya_husband"][0] + \
                                                  dolya_dict["private_dolya_husband"][0]
                        if dolya_husband_chislitel == dolya_dict["before_marriage_dolya_husband"][1]:
                            dolya_husband = 1
                        else:
                            dolya_husband = f'{dolya_husband_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                        owners[husband] = {
                            'доля': dolya_husband,
                            'совместные сособственники': wife,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                        list_of_links.append(to_link('purchase_before_marriage'))
                        list_of_links.append(to_link('purchase_marriage_private_money'))
                        list_of_links.append(to_link('common_property_sovmestnaya'))
                        list_of_links.append(to_link('common_property_dolevaya'))

                        # неообходимо сложить личные доли жены в имуществе до брака и после брака
                        dolya_wife_chislitel = dolya_dict["before_marriage_dolya_wife"][0] + \
                                               dolya_dict["private_dolya_wife"][0]
                        if dolya_wife_chislitel == dolya_dict["before_marriage_dolya_wife"][1]:
                            dolya_wife = 1
                        else:
                            dolya_wife = f'{dolya_wife_chislitel}/{dolya_dict["before_marriage_dolya_husband"][1]}'

                        owners[wife] = {
                            'доля': dolya_wife,
                            'совместные сособственники': husband,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}

            # обрабатываем вариант, если чекбокс "Часть/все деньги за имущество вносились до брака" не отмечен
            if 'before_marriage' not in form_full:
                # проверяем когда имущество приобретается полностью за общие средства
                if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' not in form_full:
                    # Если было указано, что имущество приобретается полностью за общие средства
                    # ostatok - было ли отмечено поле "полностью"
                    if form_full['common_amount'] == ['common_amount_all']:

                        owners[wife] = {
                            'доля': None,
                            'совместные сособственники': husband,
                            'совместная доля': 1}
                        list_of_links.append(to_link('common_property_sovmestnaya'))

                        owners[husband] = {'доля': None,
                                           'совместные сособственники': wife,
                                           'совместная доля': 1}

                    # Если была выбрана доля общего имущества
                    if form_full['common_amount'] == ['common_amount_dolya']:
                        dolya_dict = dolya_math(
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                            flag_ownership='ownership')

                        owners[wife] = {
                            'доля': None,
                            'совместные сособственники': husband,
                            'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                        list_of_links.append(to_link('common_property_sovmestnaya'))

                        owners[husband] = {'доля': None,
                                           'совместные сособственники': wife,
                                           'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('common_property_dolevaya'))

                # проверяем вариант, когда имущество приобретено полностью за средства жены
                if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                    # Если было указано, что имущество приобретается полностью за средства жены
                    if form_full['private_wife_amount'] == ['private_wife_amount_all']:

                        owners[wife] = {
                            'доля': 1,
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('purchase_marriage_private_money'))

                    # Если была выбрана доля
                    if form_full['private_wife_amount'] == ['private_wife_amount_dolya']:
                        dolya_dict = dolya_math(
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            flag_ownership='ownership')

                        owners[wife] = {
                            'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}

                # проверяем вариант, когда имущество приобретено полностью за средства мужа
                if 'common_dolya' not in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                    # Если было указано, что имущество приобретается полностью за средства мужа
                    if form_full['private_husband_amount'] == ['private_husband_amount_all']:
                        owners[husband] = {
                            'доля': 1,
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('purchase_marriage_private_money'))

                    # Если была выбрана доля
                    if form_full['private_husband_amount'] == ['private_husband_amount_dolya']:
                        dolya_dict = dolya_math(
                            private_dolya_husband=(
                            private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                            flag_ownership='ownership')

                        owners[husband] = {
                            'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                            'совместная доля': None}

                # проверяем вариант, когда имущество приобретено частично за общие средства и частично за средства жены
                if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' not in form_full:
                    dolya_dict = dolya_math(
                        common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                        private_dolya_wife=(
                            private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        flag_ownership='ownership')

                    owners[husband] = {
                        'доля': None,
                        'совместные сособственники': wife,
                        'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                    list_of_links.append(to_link('common_property_sovmestnaya'))

                    owners[wife] = {
                        'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                        'совместные сособственники': husband,
                        'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                    list_of_links.append(to_link('purchase_marriage_private_money'))

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

                # проверяем вариант, когда имущество приобретено частично за общие средства и частично за средства мужа
                if 'common_dolya' in form_full and 'private_wife' not in form_full and 'private_husband' in form_full:
                    dolya_dict = dolya_math(
                        common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                        private_dolya_husband=(
                            private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                        flag_ownership='ownership')

                    owners[husband] = {
                        'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                        'совместные сособственники': wife,
                        'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                    list_of_links.append(to_link('purchase_marriage_private_money'))

                    owners[wife] = {
                        'доля': None,
                        'совместные сособственники': husband,
                        'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                    list_of_links.append(to_link('common_property_sovmestnaya'))

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

                # проверяем вариант, когда имущество приобретено частично за личные средства мужа и частично за личные средства жены
                if 'common_dolya' not in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                    dolya_dict = dolya_math(
                        private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        private_dolya_husband=(
                            private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                        flag_ownership='ownership')

                    owners[husband] = {
                        'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                        'совместные сособственники': None,
                        'совместная доля': None}
                    list_of_links.append(to_link('purchase_marriage_private_money'))

                    owners[wife] = {
                        'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                        'совместные сособственники': None,
                        'совместная доля': None}

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

                # проверяем вариант, когда имущество приобретено частично за общие средства, частично за личные средства мужа и частично за личные средства жены
                if 'common_dolya' in form_full and 'private_wife' in form_full and 'private_husband' in form_full:
                    dolya_dict = dolya_math(
                        common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                        private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        private_dolya_husband=(
                            private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                        flag_ownership='ownership')

                    owners[husband] = {
                        'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                        'совместные сособственники': wife,
                        'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}
                    list_of_links.append(to_link('purchase_marriage_private_money'))
                    list_of_links.append(to_link('common_property_sovmestnaya'))

                    owners[wife] = {
                        'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                        'совместные сособственники': husband,
                        'совместная доля': f'{dolya_dict["common_dolya"][0]}/{dolya_dict["common_dolya"][1]}'}

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

        ##########
        # обрабатываем вариант, где выбрано "Создание"
        if form_full['purchase_type'] == ['purchase_type_creation']:
            owners[husband] = {'доля': None,
                               'совместные сособственники': wife,
                               'совместная доля': 1}
            owners[wife] = {'доля': None,
                            'совместные сособственники': husband,
                            'совместная доля': 1}
            list_of_links.append(to_link('sozdanie_imushestva'))
            list_of_links.append(to_link('common_property_sovmastnaya'))

        # обрабатываем вариант, где выбран "Подарок"
        if form_full['purchase_type'] == ['purchase_type_present']:
            # обрабатываем вариант, когда выбрано, что подарено было жене
            if 'present_receiver_wife' in form_full and 'present_receiver_husband' not in form_full:
                # если указано, что подарено жене в полном объеме
                if form_full['present_amount_wife'] == ['present_amount_all_wife']:
                    owners[wife] = {'доля': 1,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                    list_of_links.append(to_link('individual_property'))
                    list_of_links.append(to_link('present_imushestvo'))

                # если выбран вариант "в части"
                if form_full['present_amount_wife'] == ['present_amount_dolya_wife']:
                    dolya_dict = dolya_math(
                        private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        flag_ownership='ownership')

                    owners[wife] = {'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                    list_of_links.append(to_link('present_imushestvo'))

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

            # обрабатываем вариант, когда выбрано, что подарено было мужу
            if 'present_receiver_wife' not in form_full and 'present_receiver_husband' in form_full:
                # если указано, что подарено мужу в полном объеме
                if form_full['present_amount_husband'] == ['present_amount_all_husband']:
                    owners[husband] = {'доля': 1,
                                    'совместные сособственники': None,
                                    'совместная доля': None}
                    list_of_links.append(to_link('individual_property'))
                    list_of_links.append(to_link('present_imushestvo'))

                # если выбран вариант "в части"
                if form_full['present_amount_husband'] == ['present_amount_dolya_husband']:
                    dolya_dict = dolya_math(
                        private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                        flag_ownership='ownership')

                    owners[husband] = {
                        'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                        'совместные сособственники': None,
                        'совместная доля': None}
                    list_of_links.append(to_link('present_imushestvo'))

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))


            # обрабатываем вариант, когда выбрано, что подарено было обоим (мужу и жене)
            if 'present_receiver_wife' in form_full and 'present_receiver_husband' in form_full:
                dolya_dict = dolya_math(
                    private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                    private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                    flag_ownership='ownership')

                owners[wife] = {
                    'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                    'совместные сособственники': None,
                    'совместная доля': None}

                owners[husband] = {
                    'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                    'совместные сособственники': None,
                    'совместная доля': None}
                list_of_links.append(to_link('present_imushestvo'))

                if 'Иные сособственники' in dolya_dict:
                    owners['Иные сособственники'] = {
                        'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                        'совместные сособственники': None,
                        'совместная доля': None}
                    list_of_links.append(to_link('common_property_dolevaya'))

        # обрабатываем вариант, где выбрано "Наследование"
        if form_full['purchase_type'] == ['purchase_type_inheritance']:
            # обрабатываем вариант, когда выбрано, что имущество унаследовано женой
            if form_full['inheritance_receiver'] == ['inheritance_receiver_wife']:
                # если выбран вариант "полностью"
                owners[wife] = {
                    'доля': 1,
                    'совместные сособственники': None,
                    'совместная доля': None}
                list_of_links.append(to_link('individual_property'))
                list_of_links.append(to_link('inheritance_imushestvo'))

                # если выбран вариант "в части"
                if form_full['inheritance_amount_wife'] == ['inheritance_amount_dolya_wife']:
                    dolya_dict = dolya_math(
                        private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        flag_ownership='ownership')

                    owners[wife] = {
                        'доля': f'{dolya_dict["private_dolya_wife"][0]}/{dolya_dict["private_dolya_wife"][1]}',
                        'совместные сособственники': None,
                        'совместная доля': None}
                    list_of_links.append(to_link('inheritance_imushestvo'))

                    if 'Иные сособственники' in dolya_dict:
                        owners['Иные сособственники'] = {
                            'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('common_property_dolevaya'))

            # обрабатываем вариант, когда выбрано, что имущество унаследовано мужем
            if form_full['inheritance_receiver'] == ['inheritance_receiver_husband']:
                # обрабатываем вариант, когда выбрано, что имущество унаследовано мужем
                if form_full['inheritance_receiver'] == ['inheritance_receiver_husband']:
                    # если выбран вариант "полностью"
                    owners[husband] = {
                        'доля': 1,
                        'совместные сособственники': None,
                        'совместная доля': None}
                    list_of_links.append(to_link('individual_property'))
                    list_of_links.append(to_link('inheritance_imushestvo'))

                    # если выбран вариант "в части"
                    if form_full['inheritance_amount_husband'] == ['inheritance_amount_dolya_husband']:
                        dolya_dict = dolya_math(
                            private_dolya_wife=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband),
                            flag_ownership='ownership')

                        owners[husband] = {
                            'доля': f'{dolya_dict["private_dolya_husband"][0]}/{dolya_dict["private_dolya_husband"][1]}',
                            'совместные сособственники': None,
                            'совместная доля': None}
                        list_of_links.append(to_link('inheritance_imushestvo'))

                        if 'Иные сособственники' in dolya_dict:
                            owners['Иные сособственники'] = {
                                'доля': f'{dolya_dict["Иные сособственники"][0]}/{dolya_dict["Иные сособственники"][1]}',
                                'совместные сособственники': None,
                                'совместная доля': None}
                            list_of_links.append(to_link('common_property_dolevaya'))


########################################
    # TODO - добавить в логику "детское имущество"
    # TODO - добавить в логику "вещи личного пользования"

    type_of_relationships = {'Собственность': owners}
    i_ownership = {period_of_time: type_of_relationships}
    ownership = {'ownership': i_ownership}
    # TODO - нужно, чтобы еще возвращал list_of_links
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
        # TODO - сделать без before_marriage
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

                    # проверяем вариант, когда до брака только женой, а остаток за счет общих средств, личных средств жены и личных средств мужа
                    if 'common_dolya' in data and 'private_wife' in data and 'private_husband' in data:
                        errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife, 'личные средства жены'))
                        errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                                  'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_wife=(
                            before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                   private_dolya_znamenatel_husband),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))


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


                    # проверяем вариант, когда до брака только мужем, а остаток за счет общих средств, личных средств жены и личных средств мужа
                    if 'common_dolya' in data and 'private_wife' in data and 'private_husband' in data:
                        errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                        errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                                  'личные средства жены'))
                        errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                                  'личные средства мужа'))
                        errors.update(dolya_math(before_marriage_dolya_husband=(
                            before_marriage_dolya_chislitel_husband, before_marriage_dolya_znamenatel_husband),
                            private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                            private_dolya_husband=(private_dolya_chislitel_husband,
                                                   private_dolya_znamenatel_husband),
                            common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))

            # обрабатываем вариант, когда выбрано, что деньги вносились обоими будущими супругами
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

                # проверяем вариант, когда до брака обоими будущими супругами, а остаток за счет личных средств жены и личных средств мужа
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

                # проверяем вариант, когда до брака только обоими будущими супругами, а остаток за счет общих средств, личных средств жены и личных средств мужа
                if 'common_dolya' in data and 'private_wife' in data and 'private_husband' in data:
                    errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                    errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                              'личные средства жены'))
                    errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                              'личные средства мужа'))
                    errors.update(dolya_math(before_marriage_dolya_wife=(
                        before_marriage_dolya_chislitel_wife, before_marriage_dolya_znamenatel_wife),
                        before_marriage_dolya_husband=(before_marriage_dolya_chislitel_husband,
                                                       before_marriage_dolya_znamenatel_husband),
                        private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                        private_dolya_husband=(private_dolya_chislitel_husband,
                                               private_dolya_znamenatel_husband),
                        common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))

        # обрабатываем вариант, если чекбокс "Часть/все деньги за имущество вносились до брака" не отмечен
        if 'before_marriage' not in data:
            # проверяем когда имущество приобретается полностью за общие средства
            if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' not in data:
                # Если было указано, что имущество приобреталось полностью за счет общего имущества
                # ostatok - было ли отмечено поле "полностью"
                if data['common_amount'] == 'common_amount_all':
                    pass
                # Если была выбрана доля общего имущества
                if data['common_amount'] == 'common_amount_dolya':
                    errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                    errors.update(dolya_math(common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))

            # проверяем вариант, когда имущество приобретается за счет жены
            if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' not in data:
                # Если было указано, что имущество приобреталось полностью за счет личных средств жены
                # ostatok - было ли отмечено поле "полностью"
                if data['private_wife_amount'] == 'private_wife_amount_all':
                    pass
                # Если была выбрана "часть средств жены"
                if data['private_wife_amount'] == 'private_wife_amount_dolya':
                    errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                              'личные средства жены'))
                    errors.update(dolya_math(private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife)))

            # проверяем вариант, когда имущество приобретается за счет мужа
            if 'common_dolya' not in data and 'private_wife' not in data and 'private_husband' in data:
                # Если было указано, что имущество приобреталось полностью за счет личных средств мужа
                # ostatok - было ли отмечено поле "полностью"
                if data['private_husband_amount'] == 'private_husband_amount_all':
                    pass
                # Если была выбрана "часть средств мужа"
                if data['private_husband_amount'] == 'private_husband_amount_dolya':
                    errors.update(
                        dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                    'личные средства мужа'))
                    errors.update(dolya_math(private_dolya_husband=(private_dolya_chislitel_husband, private_dolya_znamenatel_husband)))

            # проверяем вариант, когда имущество приобреталось за счет общих средств и личных средств жены
            if 'common_dolya' in data and 'private_wife' in data and 'private_husband' not in data:
                errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                          'личные средства жены'))
                errors.update(dolya_math(common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                    private_dolya_wife=(private_dolya_chislitel_wife,
                                        private_dolya_znamenatel_wife)))

            # проверяем вариант, когда имущество приобреталось за счет общих средств и личных средств мужа
            if 'common_dolya' in data and 'private_wife' not in data and 'private_husband' in data:
                errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                          'личные средства мужа'))
                errors.update(dolya_math(common_dolya=(common_dolya_chislitel, common_dolya_znamenatel),
                    private_dolya_husband=(private_dolya_chislitel_husband,
                                           private_dolya_znamenatel_husband)))

            # проверяем вариант, когда имущество приобреталось за счет личных средств жены и личных средств мужа
            if 'common_dolya' not in data and 'private_wife' in data and 'private_husband' in data:
                errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                          'личные средства жены'))
                errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                          'личные средства мужа'))
                errors.update(dolya_math(private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                    private_dolya_husband=(private_dolya_chislitel_husband,
                                           private_dolya_znamenatel_husband)))

            # проверяем вариант, когда имущество приобреталось за счет общих средств, личных средств жены и личных средств мужа
            if 'common_dolya' in data and 'private_wife' in data and 'private_husband' in data:
                errors.update(dolya_check(common_dolya_chislitel, common_dolya_znamenatel, 'общая доля'))
                errors.update(dolya_check(private_dolya_chislitel_wife, private_dolya_znamenatel_wife,
                                          'личные средства жены'))
                errors.update(dolya_check(private_dolya_chislitel_husband, private_dolya_znamenatel_husband,
                                          'личные средства мужа'))
                errors.update(dolya_math(private_dolya_wife=(private_dolya_chislitel_wife, private_dolya_znamenatel_wife),
                    private_dolya_husband=(private_dolya_chislitel_husband,
                                           private_dolya_znamenatel_husband),
                    common_dolya=(common_dolya_chislitel, common_dolya_znamenatel)))

    # обрабатываем вариант, где выбран "Подарок"
    if data['purchase_type'] == 'purchase_type_present':
        print('Подарок')
        # обрабатываем вариант, когда выбрано, что подарено было жене
        if 'present_receiver_wife' in data and 'present_receiver_husband' not in data:
            # если выбран вариант "в части"
            if data['present_amount_wife'] == 'present_amount_dolya_wife':
                errors.update(
                    dolya_check(present_dolya_chislitel_wife, present_dolya_znamenatel_wife,
                                'доля подарка жены'))
                errors.update(dolya_math(present_dolya_wife=(
                    present_dolya_chislitel_wife, present_dolya_znamenatel_wife)))
        # обрабатываем вариант, когда выбрано, что подарено было мужу
        if 'present_receiver_wife' not in data and 'present_receiver_husband' in data:
            # если выбран вариант "в части"
            if data['present_amount_husband'] == 'present_amount_dolya_husband':
                errors.update(
                    dolya_check(present_dolya_chislitel_husband, present_dolya_znamenatel_husband,
                                'доля подарка мужа'))
                errors.update(dolya_math(present_dolya_husband=(
                    present_dolya_chislitel_husband, present_dolya_znamenatel_husband)))

        # обрабатываем вариант, когда выбрано, что подарено было обоим (мужу и жене)
        if 'present_receiver_wife' in data and 'present_receiver_husband' in data:
            errors.update(
                dolya_check(present_dolya_chislitel_wife, present_dolya_znamenatel_wife,
                            'доля подарка жены'))
            errors.update(
                dolya_check(present_dolya_chislitel_husband, present_dolya_znamenatel_husband,
                            'доля подарка мужа'))
            errors.update(dolya_math(present_dolya_wife=(
                present_dolya_chislitel_wife, present_dolya_znamenatel_wife),
                present_dolya_husband=(
                present_dolya_chislitel_husband, present_dolya_znamenatel_husband)))

    # обрабатываем вариант, где выбрано "Наследование"
    if data['purchase_type'] == 'purchase_type_inheritance':
        print('Наследство')
        # обрабатываем вариант, когда выбрано, что имущество унаследовано женой
        if data['inheritance_receiver'] == 'inheritance_receiver_wife':
            # если выбран вариант "в части"
            if data['inheritance_amount_wife'] == 'inheritance_amount_dolya_wife':
                errors.update(
                    dolya_check(inheritance_dolya_chislitel_wife, inheritance_dolya_znamenatel_wife,
                                'доля имущества, полученная в наследство женой'))
                errors.update(dolya_math(inheritance_dolya_wife=(
                    inheritance_dolya_chislitel_wife, inheritance_dolya_znamenatel_wife)))

        # обрабатываем вариант, когда выбрано, что имущество унаследовано мужем
        if data['inheritance_receiver'] == 'inheritance_receiver_husband':
            # если выбран вариант "в части"
            if data['inheritance_amount_husband'] == 'inheritance_amount_dolya_husband':
                errors.update(
                    dolya_check(inheritance_dolya_chislitel_husband, inheritance_dolya_znamenatel_husband,
                                'доля имущества, полученная в наследство мужем'))
                errors.update(dolya_math(inheritance_dolya_husband=(
                    inheritance_dolya_chislitel_husband, inheritance_dolya_znamenatel_husband)))


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
        if int(chislitel) > int(znamenatel):
            errors[f'Числитель в поле "{where}" не может быть больше знаменателя'] = f'{chislitel}/{znamenatel}'
        elif int(chislitel) == int(znamenatel):
            errors[f'Числитель в поле "{where}" не может быть равен знаменателю. Выберите пункт "полностью"'] = f'{chislitel}/{znamenatel}'
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
               ostatok=False,
               flag_ownership=None):


    dolya_dict_temp = locals().copy()
    del dolya_dict_temp['ostatok']
    del dolya_dict_temp['flag_ownership']
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

    #print(list_of_chislitels)
    #print(list_of_znamenatels)
    #print(dolya_dict)

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
    else:

        for i in range(len(list_of_znamenatels)):
            # находим общий знаменатель всех знаменателей, которые ввел пользователь
            if i == 0:
                temp_znam = list_of_znamenatels[i]
            else:
                #znam = (list_of_znamenatels[i] * list_of_znamenatels[i-1] // gcd(list_of_znamenatels[i], list_of_znamenatels[i-1]))
                znam = (list_of_znamenatels[i] * temp_znam // gcd(list_of_znamenatels[i], temp_znam))
                temp_znam = znam
            #print(znam)

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
            if ostatok == True:
                dolya_dict['Остаток'] = (znam - summ, znam)
            else:
                dolya_dict['Иные сособственники'] = (znam - summ, znam)

    if flag_ownership == None:
        return errors
    # TODO - нужно вернуть значение dolya_dict и errors, если эта функция будет использоваться при добавлении долей в БД
    elif flag_ownership == 'ownership':
        return dolya_dict

def to_link(text_link):
    '''
    Функция для сокращения 3-х строк в одну. Функция принимает ключ в словаре с константами ссылок links_and_texts.py
    и возвращает готовый link, который нужно будет добавить с список link'ов
    :param text_link: ключ словаря TEXTS с нормами права в links_and_texts.py
    :return: готовая ссылка
    '''
    link_name, law_link, law_text, npa = TEXTS[text_link]
    link = Link(link_name, law_link, law_text, npa)
    return link

