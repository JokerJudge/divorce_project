import datetime
from dataclasses import dataclass, field
from typing import List
'''
Модуль описания нормативных правовых актов (class NPA), ссылок (class Link)
'''

@dataclass
class NPA:
    '''
    Класс, описывающий нормативный правовой акт (НПА), т.е. законы, приказы, указы и т.п.
    :param initial_date: дата принятия НПА
    :param number: номер НПА
    :param title: название НПА
    :param type_of_act: вид акта (Приказ, Федеральный закон, Федеральный конституционный закон и т.п.)
    :param short_title: короткое общепринятое название (ФЗ № 44, ФЗ № 135, ГК РФ и т.п.)
    :param office: орган, принявший акт
    :param area: уровень (федеральный, региональный, муниципальный)
    :param norms: список связанных норм права
    '''
    initial_date: datetime.date = field(repr=False)
    number: str = field(repr=False)
    title: str = field(repr=False)
    type_of_act: str = field(repr=False)
    short_title: str
    office: str = field(repr=False)
    area: str = field(repr=False)
    norms: List[str] = field(repr=False, init=False, default_factory=list)

    def __str__(self):
        return self.short_title

'''
    def __init__(self,
                 initial_date: datetime.date,
                 number: str,
                 title: str,
                 type_of_act: str,
                 short_title: str,
                 office: str,
                 area: str):
        self.initial_date = initial_date
        self.number = number
        self.title = title
        self.type_of_act = type_of_act
        self.short_title = short_title
        self.office = office
        self.area = area
        self.norms = []
'''

family_code = NPA(datetime.date(1995, 12, 29), '223-ФЗ', 'Семейный кодекс Российской Федерации', 'Кодекс', 'Семейный кодекс РФ', 'Государственная Дума РФ', 'Федеральный')

@dataclass
class Link:
    '''
    Класс, описывающий ссылки на нормы права
    :param law_link: Ссылка на норму права
    :param law_text: Цитата из текста НПА
    :param npa: указание на нормативный правовой акт
    :param errors: список ошибок при обработке юридической логики
    '''
    law_link: str
    law_text: str = field(repr=False)
    npa: NPA = field(repr=False, default=family_code)
    errors: List[str] = field(repr=False, init=False, default_factory=list)

    def __str__(self):
        return self.law_link
'''
    def __init__(self, law_link: str, law_text: str, npa: NPA = family_code):
        self.law_link = law_link
        self.law_text = law_text
        self.npa = npa
        self.errors = []

    def __str__(self):
        return self.law_link
'''