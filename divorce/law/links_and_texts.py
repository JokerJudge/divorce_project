import datetime
from .law import NPA, Link
'''
Файл для хранения констант, связанных с нормами права
'''
#Нормативные акты
#Семейный кодекс РФ
family_code = NPA(datetime.date(1995, 12, 29), '223-ФЗ', 'Семейный кодекс Российской Федерации', 'Кодекс', 'Семейный кодекс РФ', 'Семейного кодекса РФ', 'Государственная Дума РФ', 'Федеральный')
#Гражданский кодекс РФ
civil_code = NPA(datetime.date(1994, 11, 30), '51-ФЗ', 'Гражданский кодекс Российской Федерации', 'Кодекс', 'Гражданский кодекс РФ', 'Гражданского кодекса РФ', 'Государственная Дума РФ', 'Федеральный')

#Постановление Пленума ВС РФ о расторжении брака
VS_break_up = NPA(datetime.date(1998, 11, 5), '15', 'Постановление Пленума Верховного Суда Российской Федерации', 'Постановление',
                  'Пленум ВС РФ № 15', 'Постановления Пленума ВС РФ № 15', 'Верховный Суд РФ', 'Федеральный')

VS_obzor_2_2017 = NPA(datetime.date(2017, 4, 26), '2', 'Обзор судебной практики Верховного Суда Российской Федерации', 'Обзор',
                  'Обзор ВС РФ № 2(2017)', 'Обзора судебной практики ВС РФ № 2(2017)', 'Верховный Суд РФ', 'Федеральный')

OBJECTS_OF_CIVIL_LAW = {'NEDVIZHIMOST': ['Квартира',
                                         'Дом с земельным участком',
                                         'Земельный участок',
                                         'Дом без земли',
                                         'Иная недвижимая вещь'],
                        'DVIZHIMAYA_VESH': ['Автомобиль',
                                            'Деньги наличные',
                                            'Иная движимая вещь'],
                        'RID': ['Результаты интеллектуальной деятельности'],
                        'INOE_IMUSHESTVO': ['Деньги безналичные', 'Иное имущество']
                        }
# using in models.py
PURCHASE_TYPE_CHOICES = [('Покупка', 'Покупка'),
                         ('Подарок', 'Подарок'),
                         ('Создание', 'Создание'),
                         ('Наследство', 'Наследство')]
# using in models.py
TYPES_OF_PROPERTY_CHOICES = [('Квартира', 'Квартира'),
                             ('Дом с земельным участком', 'Дом с земельным участком'),
                             ('Дом без земли', 'Дом без земли'),
                             ('Земельный участок', 'Земельный участок'),
                             ('Автомобиль', 'Автомобиль'),
                             ('Деньги наличные', 'Деньги наличные'),
                             ('Деньги безналичные', 'Деньги безналичные'),
                             ('Иная недвижимая вещь', 'Иная недвижимая вещь'),
                             ('Иная движимая вещь', 'Иная движимая вещь'),
                             ('Результаты интеллектуальной деятельности', 'Результаты интеллектуальной деятельности'),
                             ('Иное имущество', 'Иное имущество')]

# использовано в property.py
TYPES_OF_PROPERTY_RELATIONS = {'Собственность': ['Доля',
                                                 'Совместные сособственники',
                                                 'Совместная доля'],
                               'Аренда': []}

#link_name, law_link, law_text, npa
TEXTS = {'sex_verification': ('Проверка на пол вступающих в брак',
                              'ч.1 ст. 12',
                              'Для заключения брака необходимы взаимное добровольное согласие мужчины и женщины,'
                              ' вступающих в брак...',
                              family_code),
         'age_verification': ('Проверка на возраст вступления в брак',
                              'ч.1 ст. 13',
                              'Брачный возраст устанавливается в восемнадцать лет',
                              family_code),
         'another_marriage_verification': ('Проверка на наличие другого брака в заданный период',
                                           'ч.2 ст. 12, абзац 2 ч.1 ст. 14',
                                           'Не допускается заключение брака между лицами, из которых хотя бы одно лицо'
                                           ' уже состоит в другом зарегистрированном браке',
                                           family_code),
         'type_of_property_func': ('Проверка на тип имущества',
                                   'ст. 128',
                                   'К объектам гражданских прав относятся вещи (включая наличные деньги и документарные'
                                   ' ценные бумаги), иное имущество, в том числе имущественные права (включая безналичные'
                                   ' денежные средства, бездокументарные ценные бумаги, цифровые права); результаты работ'
                                   ' и оказание услуг; охраняемые результаты интеллектуальной деятельности и приравненные'
                                   ' к ним средства индивидуализации (интеллектуальная собственность); нематериальные блага.',
                                   civil_code),
         'marriage_periods': ('Проверка на пересечение даты приобретения имущества с датами брака',
                              'ч.1 ст. 34',
                              'Имущество, нажитое супругами во время брака, является их совместной собственностью',
                              family_code),
         'purchase_after_break_up': ('Приобретение имущества произошло после фактического прекращения брачных отношений',
                                     'ч.4 ст.38',
                                     'Суд может признать имущество, нажитое каждым из супругов в период их раздельного'
                                     ' проживания при прекращении семейных отношений, собственностью каждого из них',
                                     family_code),
         'common_property': ('Возникновение общей собственности',
                             'п.1 ст. 244',
                             'Имущество, находящееся в собственности двух или нескольких лиц, принадлежит им на праве общей собственности',
                             civil_code),
         'common_property_dolevaya': ('Возникновение общей долевой собственности',
                             'п.3 ст. 244',
                             ' Общая собственность на имущество является долевой, за исключением случаев, когда законом предусмотрено образование'
                             ' совместной собственности на это имущество',
                             civil_code),
         'common_property_sovmestnaya': ('Возникновение общей совместной собственности',
                             'ч.1 ст. 34',
                             'Имущество, нажитое супругами во время брака, является их совместной собственностью',
                             family_code),
         'individual_property': ('Возникновение личной собственности',
                             'п.1 ст. 213',
                             'В собственности граждан и юридических лиц может находиться любое имущество, за исключением'
                             ' отдельных видов имущества, которое в соответствии с законом не может принадлежать'
                             ' гражданам или юридическим лицам',
                             civil_code),
         'purchase_before_marriage': ('Средства за покупку внесены до заключения брака',
                             'абз. 4 п.15',
                             'Не является общим совместным имущество, приобретенное хотя и во время брака, но на личные'
                             ' средства одного из супругов, принадлежавшие ему до вступления в брак, полученное в дар '
                             'или в порядке наследования, а также вещи индивидуального пользования, за исключением'
                             ' драгоценностей и других предметов роскоши (ст. 36 СК РФ)',
                             VS_break_up),
         'purchase_marriage_private_money': ('Приобретение имущества на личные средства в период брака',
                             'п.10',
                             'На имущество, приобретенное в период брака, но на средства, принадлежавшие одному из'
                             ' супругов лично, режим общей совместной собственности супругов не распространяется',
                             VS_obzor_2_2017),
         'sozdanie_imushestva': ('Созадание имущества',
                                 'п.1 ст. 218',
                                 'Право собственности на новую вещь, изготовленную или созданную лицом для себя с '
                                 'соблюдением закона и иных правовых актов, приобретается этим лицом',
                                 civil_code),
         'present_imushestvo': ('Имущество приобретено в дар',
                                'ч.1 ст. 36',
                                'Имущество, принадлежавшее каждому из супругов до вступления в брак, а также имущество,'
                                ' полученное одним из супругов во время брака в дар, в порядке наследования или по иным'
                                ' безвозмездным сделкам (имущество каждого из супругов), является его собственностью',
                                family_code),
         'inheritance_imushestvo': ('Имущество приобретено в порядке наследования',
                                    'ч.1 ст. 36',
                                    'Имущество, принадлежавшее каждому из супругов до вступления в брак, а также имущество,'
                                    ' полученное одним из супругов во время брака в дар, в порядке наследования или по иным'
                                    ' безвозмездным сделкам (имущество каждого из супругов), является его собственностью',
                                    family_code),
         'individual_use_vesh': ('Вещь индивидуального пользования',
                                 'ч.2 ст. 36',
                                 'Вещи индивидуального пользования (одежда, обувь и другие), за исключением'
                                 ' драгоценностей и других предметов роскоши, хотя и приобретенные в период брака'
                                 ' за счет общих средств супругов, признаются собственностью того супруга, который ими пользовался',
                                 family_code)
         }