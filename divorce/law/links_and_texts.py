import datetime
from .law import NPA, Link
'''
Файл для хранения констант, связанных с нормами права
'''

#Семейный кодекс РФ
family_code = NPA(datetime.date(1995, 12, 29), '223-ФЗ', 'Семейный кодекс Российской Федерации', 'Кодекс', 'Семейный кодекс РФ', 'Семейного кодекса РФ', 'Государственная Дума РФ', 'Федеральный')

#law_link, law_text, npa
TEXTS = {'sex_verification': ('ч.1 ст. 12',
                              'Для заключения брака необходимы взаимное добровольное согласие мужчины и женщины,'
                              ' вступающих в брак...',
                              family_code),
         'age_verification': ('ч.1 ст. 13',
                              'Брачный возраст устанавливается в восемнадцать лет',
                              family_code),
         'another_marriage_verification': ('ч.2 ст. 12, абзац 2 ч.1 ст. 14',
                                           'Не допускается заключение брака между лицами, из которых хотя бы одно лицо'
                                           ' уже состоит в другом зарегистрированном браке',
                                           family_code)}