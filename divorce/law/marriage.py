import datetime
from ..models import *
from .law import *
'''
модуль делающий проверки в соответствии с законодательством РФ
на соответствие брака необходимым требованиям
'''

def law(person_1: Fiz_l,
        person_2: Fiz_l,
        date_of_marriage_registration: datetime.date,
        marriage: Marriage):
    '''
    Общая функция, куда подаются сведения из cleaned_data, введенных пользователем при добавлении брака
    :param person_1: выбранное пользователем лицо № 1
    :param person_2: выбранное пользователем лицо № 2
    :param date_of_marriage_registration: выбранная пользователем дата регистрации брака
    :return: True, если все проверки пройдены - можно сохранять в БД
    False - ошибки, которые должны быть показаны пользователю
    '''
    # список необходимых в соответствии с законом проверок
    # TODO - добавить в list_of_rules another_marriage_verification
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

def sex_verification(person_1: Fiz_l, person_2: Fiz_l):
    '''
    Проверка на отсутствие однополого брака (ч.1 ст.12 СК РФ)
    :return: True + law_link (запись о прошедшей проверке), если М + Ж
    False, если М + М или Ж + Ж
    '''
    law_link = 'ч.1 ст. 12 Семейного кодекса РФ'
    law_text = 'Для заключения брака необходимы взаимное добровольное ' \
               'согласие мужчины и женщины, вступающих в брак...'
    link = Link(law_link, law_text)
    if person_1.sex != person_2.sex:
        return True, link
    else:
        link.errors.append(f'{person_1} и {person_2} одного пола. Брак невозможен')
        return False, link

def age_verification(person_1: Fiz_l, person_2: Fiz_l, date_of_marriage_registration: datetime.date):
    '''
    Проверка на достижение лицами брачного возраста
    #TODO - законами субъекта может быть установлен более ранний брачный возраст
    :param person_1: лицо № 1
    :param person_2: лицо № 2
    :param date_of_marriage_registration: дата заключения брака
    :return: True, если оба лица соответствуют требованиям к брачному возрасту
    False, если есть проблемы с возрастом
    '''
    law_link = 'ч.1 ст. 13 Семейного кодекса РФ'
    law_text = '''Брачный возраст устанавливается в восемнадцать лет'''
    link = Link(law_link, law_text)
    marriage_age = 18
    for i in [person_1, person_2]:
        temp_date = i.date_of_birth.replace(date_of_marriage_registration.year) # timedelta работает с днями, поэтому вводим врем. переменную
        if temp_date > date_of_marriage_registration: # если ДР будет после даты брака
            i.marriage_age = date_of_marriage_registration.year - i.date_of_birth.year - 1
        else:
            i.marriage_age = date_of_marriage_registration.year - i.date_of_birth.year
        if i.marriage_age < marriage_age:
            link.errors.append(f'{i} не достиг(ла) брачного возраста ({marriage_age} лет) на момент вступления в брак {date_of_marriage_registration}')
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
    law_link = 'ч.2 ст. 12 Семейного кодекса РФ, абзац 2 ч.1 ст. 14 Семейного кодекса РФ'
    law_text = '''Не допускается заключение брака между лицами, из которых хотя бы одно лицо уже состоит в другом зарегистрированном браке'''
    link = Link(law_link, law_text)

    for i in [person_1, person_2]:
        if i.marriages.all():
            list_of_marriages = list(i.marriages.all())
            for j in list_of_marriages:
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