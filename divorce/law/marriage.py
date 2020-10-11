'''
Этот файл — часть divorce_project.

divorce_project -- веб-сервис по моделированию имущественных последствий для лица
на случай вступления в брак и развода по законодательству Российской Федерации
Copyright © 2020 Evgenii Kovalenko <kovalenko_evgeny@bk.ru>

divorce_project - свободная программа: вы можете перераспространять ее и/или
изменять ее на условиях Афферо Стандартной общественной лицензии GNU в том виде,
в каком она была опубликована Фондом свободного программного обеспечения;
либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
версии.

divorce_project распространяется в надежде, что она будет полезной,
но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Афферо Стандартной
общественной лицензии GNU.

Вы должны были получить копию Афферо Стандартной общественной лицензии GNU
вместе с этой программой. Если это не так, см.
<https://www.gnu.org/licenses/>.)
'''

import datetime
import dateutil.relativedelta as relativedelta
from ..models import *
from .law import *
from .links_and_texts import *
'''
модуль делающий проверки в соответствии с законодательством РФ
на соответствие брака необходимым требованиям
'''

def marriage_law(person_1: Fiz_l,
        person_2: Fiz_l,
        date_of_marriage_registration: datetime.date,
        marriage: Marriage):
    '''
    Общая функция, куда подаются сведения из cleaned_data, введенных пользователем в формах по добавлению/
    редактированию физ.лица/брака.
    Функция содержит список других функций, которые должны быть пройдены, чтобы всё соответствовало
    законодательству

    :param person_1: выбранное пользователем лицо № 1
    :param person_2: выбранное пользователем лицо № 2
    :param date_of_marriage_registration: выбранная пользователем дата регистрации брака
    :param marriage: брак (если вносятся изменения), иначе None
    :return: True, если все проверки пройдены - можно сохранять в БД
    False - ошибки, которые должны быть показаны пользователю
    '''
    list_of_rules = [sex_verification(person_1, person_2),
                     age_verification(person_1, person_2, date_of_marriage_registration),
                     another_marriage_verification(person_1, person_2, date_of_marriage_registration, marriage)]
    # список пройденных проверок в виде списка объектов класса Link (law/law.py)
    list_of_links = []

    # последовательно проходим список проверок и на каждой итерации проверяем, всё ли ок.
    # если встречаем False, возвращаем ошибку и в БД ничего не записываем

    for i in list_of_rules:
        resolution, link = i
        list_of_links.append(link)
        if resolution is True:
            continue
        else:
            return False, list_of_links
    return True, list_of_links

def person_edit_check(person_1: Fiz_l):
    '''
    Функция для проверки ситуации, когда редактируется физическое лицо. Необходимо, чтобы при редактировании
    не получилось так, что лицо вступило в брак до наступления брачного возраста
    :param person_1:
    :param person_2:
    :param date_of_marriage_registration:
    :return:
    '''
    if hasattr(person_1, 'marriages'):
        for i in person_1.marriages.all():
            for j in i.parties.all():
                if j.id == person_1.id:
                    continue
                else:
                    person_2 = j
            date_of_marriage_registration = i.date_of_marriage_registration
            # список необходимых в соответствии с законом проверок
            list_of_rules = [age_verification(person_1, person_2, date_of_marriage_registration)]
            list_of_links = []
            resolution, link = list_of_rules[0]
            list_of_links.append(link)
            if resolution is True:
                continue
            else:
                return False, list_of_links
        list_of_links = []
        return True, list_of_links
    # если браков нет
    else:
        link_name, law_link, law_text, npa = TEXTS['age_verification']
        link = Link(link_name, law_link, law_text, npa)
        list_of_links = []
        list_of_links.append(link)
        return True, list_of_links

def sex_verification(person_1: Fiz_l, person_2: Fiz_l):
    '''
    Проверка на отсутствие однополого брака (ч.1 ст.12 СК РФ)
    :return: True + law_link (запись о прошедшей проверке), если М + Ж
    False, если М + М или Ж + Ж
    '''
    link_name, law_link, law_text, npa = TEXTS['sex_verification']
    link = Link(link_name, law_link, law_text, npa)
    if person_1.sex != person_2.sex:
        return True, link
    else:
        link.errors.append(f'{person_1} и {person_2} одного пола. Брак невозможен')
        return False, link

def age_verification(person_1: Fiz_l, person_2: Fiz_l, date_of_marriage_registration: datetime.date):
    '''
    Проверка на достижение лицами брачного возраста
    :param person_1: лицо № 1
    :param person_2: лицо № 2
    :param date_of_marriage_registration: дата заключения брака
    :return: True, если оба лица соответствуют требованиям к брачному возрасту
    False, если есть проблемы с возрастом
    '''
    link_name, law_link, law_text, npa = TEXTS['age_verification']
    link = Link(link_name, law_link, law_text, npa)
    marriage_age = 18
    for i in [person_1, person_2]:
        # вычисляем количество полных лет на момент заключения брака
        i.marriage_age = relativedelta.relativedelta(date_of_marriage_registration, i.date_of_birth).years
        if i.marriage_age < marriage_age:
            link.errors.append(f'{i} не достиг(ла) брачного возраста ({marriage_age} лет) на момент вступления в брак. Дата рождения: {i.date_of_birth}')
            return False, link
    return True, link

def another_marriage_verification(person_1: Fiz_l, person_2: Fiz_l, date_of_marriage_registration: datetime.date, marriage: Marriage):
    '''
    Проверка на наличие другого нерасторгнутого брака
    :param person_1: лицо № 1
    :param person_2: лицо № 2
    :param date_of_marriage_registration: дата заключения брака
    :return: True, если у обоих лиц отсутствует нерасторгнутый брак на дату регистрации нового брака
    False, если у кого-нибудь из лиц есть нерасторгнутый брак
    '''
    link_name, law_link, law_text, npa = TEXTS['another_marriage_verification']
    link = Link(link_name, law_link, law_text, npa)

    for i in [person_1, person_2]:
        if i.marriages:
            for j in i.marriages.all():
                # если в БД, то marriage = True, если это новый брак, то marriage = None
                # рассматриваем варианты, если проверке подлежит уже имеющийся в БД брак
                if marriage:
                    # если это тот же брак (при корректировке текущего брака)
                    if j.id == marriage.id:
                        continue
                    # рассматриваем варианты, когда меняется имеющийся в БД брак, который был расторгнут
                    # сравниваемый брак также расторгнут
                    if marriage.date_of_marriage_divorce and j.date_of_marriage_divorce:
                        #сравниваемый брак был расторгнут ранее даты регистрации изменяемого
                        if j.date_of_marriage_divorce < marriage.date_of_marriage_registration:
                            continue
                        #сравниваемый брак был заключен позже расторжения изменяемого брака
                        elif marriage.date_of_marriage_divorce < j.date_of_marriage_registration:
                            continue
                        else:
                            link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Периоды браков пересекаются. Измените даты прежнего, либо текущего брака.')
                            return False, link
                    #рассматриваем варианты, когда меняется имеющийся в БД брак, который был расторгнут
                    # сравниваемый брак не был расторгнут
                    elif marriage.date_of_marriage_divorce:
                        #сравниваемый брак был расторгунт до регистрации следующего
                        if marriage.date_of_marriage_divorce < j.date_of_marriage_registration:
                            continue
                        elif j.date_of_marriage_registration < marriage.date_of_marriage_registration:
                            link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Брак, начавшийся ранее не был расторгнут.')
                            return False, link
                        else:
                            link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Периоды браков пересекаются. Измените даты прежнего, либо текущего брака.')
                            return False, link
                    # рассматриваем варианты, когда меняется имеющийся в БД брак, который не был расторгнут
                    else:
                        # если сравниваемый брак был расторгнут
                        if j.date_of_marriage_divorce:
                            if j.date_of_marriage_divorce < marriage.date_of_marriage_registration:
                                continue
                            else:
                                link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Периоды браков пересекаются. Измените даты прежнего, либо текущего брака.')
                                return False, link
                        #если сравниваемый брак и меняющийся брак не были расторгнуты
                        else:
                            link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Периоды браков пересекаются. Измените даты прежнего, либо текущего брака.')
                            return False, link
                #рассматриваем варианты, когда проверяется новый брак
                else:
                    # если сравниваемый брак был расторгнут
                    if j.date_of_marriage_divorce:
                        if j.date_of_marriage_divorce < date_of_marriage_registration:
                            continue
                        elif date_of_marriage_registration < j.date_of_marriage_registration:
                            link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Мы не можем добавить брак до момента регистрации другого брака. Сначала удалите {j} и заполняйте сведения начиная с самого раннего брака {i}')
                            return False, link
                        else:
                            link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Периоды браков пересекаются. Измените даты прежнего, либо нового брака.')
                            return False, link
                    # если сравниваемый брак и меняющийся брак не были расторгнуты
                    else:
                        link.errors.append(f'{i} состоит в другом зарегистрированном браке ({j}). Периоды браков пересекаются. Измените даты прежнего, либо нового брака.')
                        return False, link
    return True, link