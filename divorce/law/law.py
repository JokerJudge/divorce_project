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
    :param short_title_for_link: короткое общепринятое название (self.short.title) в родительном падеже
    :param office: орган, принявший акт
    :param area: уровень (федеральный, региональный, муниципальный)
    :param norms: список связанных норм права
    '''
    initial_date: datetime.date = field(repr=False)
    number: str = field(repr=False)
    title: str = field(repr=False)
    type_of_act: str = field(repr=False)
    short_title: str
    short_title_for_link: str = field(repr=False)
    office: str = field(repr=False)
    area: str = field(repr=False)
    norms: List[str] = field(repr=False, init=False, default_factory=list)

    def __str__(self):
        return self.short_title

family_code = NPA(datetime.date(1995, 12, 29), '223-ФЗ', 'Семейный кодекс Российской Федерации', 'Кодекс', 'Семейный кодекс РФ', 'Семейного кодекса РФ', 'Государственная Дума РФ', 'Федеральный')

@dataclass
class Link:
    '''
    Класс, описывающий ссылки на нормы права
    :param law_link: Ссылка на норму права
    :param law_text: Цитата из текста НПА
    :param npa: указание на нормативный правовой акт
    :param errors: список ошибок при обработке юридической логики
    '''
    link_name: str
    law_link: str
    law_text: str = field(repr=False)
    npa: NPA = field(repr=False)
    errors: List[str] = field(repr=False, init=False, default_factory=list)

    def __str__(self):
        return f'{self.law_link} {self.npa.short_title_for_link}'