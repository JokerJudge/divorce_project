import datetime
from ..models import *
'''
модуль делающий проверки в соответствии с законодательством РФ
на соответствие брака необходимым требованиям
'''

def law(person_1: Fiz_l, person_2: Fiz_l, date_of_marriage_registration: datetime.date):
    '''
    Общая функция, куда подаются сведения из cleaned_data, введенных пользователем при добавлении брака
    :param person_1: выбранное пользователем лицо № 1
    :param person_2: выбранное пользователем лицо № 2
    :param date_of_marriage_registration: выбранная пользователем дата регистрации брака
    :return: True, если все проверки пройдены - можно сохранять в БД
    False - ошибки, которые должны быть показаны пользователю
    '''
    resolution, law_link = sex_verification(person_1, person_2)
    if resolution is not True:
        return False, law_link
    else:
        return True, law_link



def list_of_rules():
    '''
    Список норм права, которым должны быть проверены данные пользователя.
    :return:
    '''
    '''
    sex_verification - label (проверка на пол)
    1) ч.1 ст. 12 СК РФ
    
    '''

    pass

def sex_verification(person_1: Fiz_l, person_2: Fiz_l):
    '''
    Проверка на отсутствие однополого брака (ч.1 ст.12 СК РФ)
    :return: True + law_link (запись о прошедшей проверке), если М + Ж
    False, если М + М или Ж + Ж
    '''
    law_link = 'ч.1 ст. 12 Семейного кодекса РФ'
    if person_1.sex != person_2.sex:
        return True, law_link
    else:
        return False, law_link

