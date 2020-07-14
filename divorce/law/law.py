import datetime
'''
Модуль описания нормативных правовых актов (class NPA), ссылок (class Link)
'''

class NPA:
    def __init__(self,
                 initial_date: datetime.date,
                 number: str,
                 title: str,
                 type_of_act: str,
                 short_title: str,
                 office: str,
                 area: str):
        '''
        Класс, описывающий нормативный правовой акт (НПА), т.е. законы, приказы, указы и т.п.
        :param initial_date: дата принятия НПА
        :param number: номер НПА
        :param title: название НПА
        :param type_of_act: вид акта (Приказ, Федеральный закон, Федеральный конституционный закон и т.п.)
        :param short_title: короткое общепринятое название (ФЗ № 44, ФЗ № 135, ГК РФ и т.п.)
        :param office: орган, принявший акт
        :param area: уровень (федеральный, региональный, муниципальный)
        '''
        self.initial_date = initial_date
        self.number = number
        self.title = title
        self.type_of_act = type_of_act
        self.short_title = short_title
        self.office = office
        self.area = area
        self.norms = []

    def __str__(self):
        return self.short_title

family_code = NPA(datetime.date(1995, 12, 29), '223-ФЗ', 'Семейный кодекс Российской Федерации', 'Кодекс', 'СК РФ', 'Государственная Дума РФ', 'Федеральный')

print(family_code.norms)

class Link:
    def __init__(self, law_link: str, law_text: str, npa: NPA = family_code):
        '''
        Класс, описывающий ссылки на нормы права
        :param law_link: Ссылка на норму права
        :param law_text: Цитата из текста НПА
        :param npa: указание на нормативный правовой акт
        '''
        self.law_link = law_link
        self.law_text = law_text
        self.npa = npa
        self.errors = []

    def __str__(self):
        return self.law_link