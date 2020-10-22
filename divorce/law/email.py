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

from django.conf import settings
from django.core.mail import send_mail
#from django.template.loader import render_to_string

def send_email():
    #msg = render_to_string('path\to\template.html', {'test_variable': 'xxx'})
    send_mail('Тестовая тема', 'Тестовое письмо', settings.EMAIL_HOST_USER, ['smth@smth.com'])
