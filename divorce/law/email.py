from django.conf import settings
from django.core.mail import send_mail
#from django.template.loader import render_to_string

def send_email():
    #msg = render_to_string('path\to\template.html', {'test_variable': 'xxx'})
    send_mail('Тестовая тема', 'Тестовое письмо', settings.EMAIL_HOST_USER, ['smth@smth.com'])
