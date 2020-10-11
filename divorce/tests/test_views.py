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
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from divorce.models import Fiz_l, Marriage, Property, Distribution


class TestViews(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='django_test_user',
                                             password='password',
                                             email='jdsjks@mail.ru')
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М',
                                            service_user=self.user)
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж',
                                            service_user=self.user)
        self.marriage_1 = Marriage.objects.create(date_of_marriage_registration='2015-1-1',
                                                  date_of_marriage_divorce='2015-4-3',
                                                  service_user=self.user)
        self.marriage_1.parties.add(self.fiz_l_1, self.fiz_l_2)
        self.property_1 = Property.objects.create(name='Test_квартира',
                                                  type_of_property_form='Квартира',
                                                  date_of_purchase='2017-3-5',
                                                  obtaining_person=self.fiz_l_1,
                                                  price='4000000',
                                                  service_user=self.user)
        self.distribution_1 = Distribution.objects.create(date_of_distribution='2020-10-6',
                                                          service_user=self.user)
        self.distribution_1.parties.add(self.fiz_l_1, self.fiz_l_2)
        self.client = Client()

        self.divorce_url = reverse('main')
        self.delete_person_url = reverse('delete_person', args=[self.fiz_l_1.id])
        self.form_add_fiz_l_url = reverse('form_add_fiz_l')
        self.person_update_url = reverse('person_update', args=[self.fiz_l_1.id])
        self.form_add_marriage_url = reverse('form_add_marriage')
        self.delete_marriage_url = reverse('delete_marriage', args=[self.marriage_1.id])
        self.marriage_update_url = reverse('marriage_update', args=[self.marriage_1.id])
        self.marriage_divorce_url = reverse('marriage_divorce', args=[self.marriage_1.id])
        self.form_add_property_url = reverse('form_add_property_1')
        self.delete_property_url = reverse('delete_property', args=[self.property_1.id])
        self.property_update_url = reverse('property_update', args=[self.property_1.id])
        self.property_2_nm_url = reverse('property_2_nm')
        self.property_2_nm_update_url = reverse('property_2_nm_update', args=[self.property_1.id])
        self.property_2_m_url = reverse('property_2_m')
        self.property_2_m_update_url = reverse('property_2_m_update', args=[self.property_1.id])
        self.form_add_distribution_url = reverse('form_add_distribution')
        self.delete_distribution_url = reverse('delete_distribution', args=[self.distribution_1.id])
        self.signup_url = reverse('signup')


    def test_Divorce_GET(self):
        response = self.client.get(self.divorce_url)
        self.assertEquals(response.status_code, 200)

    def test_Divorce_template_GET(self):
        response = self.client.get(self.divorce_url)
        self.assertTemplateUsed(response, 'divorce/divorce.html')

    def test_delete_person_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.delete_person_url)
        # print(response)
        # print(response.request)
        self.assertEquals(response.status_code, 302)

    def test_form_add_Fiz_l_GET(self):
        #User = get_user_model()
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_fiz_l_url, follow=True)
        #self.user = User.objects.get(username='django_test_user')
        # print(dir(self.user))
        # print(response.context.keys())
        # print(dir(response.context['user']))
        self.assertEquals(response.status_code, 200)

    def test_form_add_Fiz_l_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_fiz_l_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_fiz_l.html')

    def test_update_person_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.person_update_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_update_person_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.person_update_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_fiz_l.html')

    def test_form_add_marriage_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_marriage_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_form_add_marriage_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_marriage_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_marriage.html')

    def test_delete_marriage_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.delete_marriage_url)
        self.assertEquals(response.status_code, 302)

    def test_marriage_update_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.marriage_update_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_marriage_update_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.marriage_update_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_marriage.html')

    def test_marriage_divorce_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.marriage_divorce_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_marriage_divorce_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.marriage_divorce_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_marriage_divorce.html')

    def test_form_add_property_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_property_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_form_add_property_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_property_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_property_1.html')

    def test_delete_property_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.delete_property_url)
        self.assertEquals(response.status_code, 302)

    def test_property_update_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_update_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_property_update_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_update_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_property_1.html')

    def test_property_2_nm_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_nm_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_property_2_nm_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_nm_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_property_2_nm.html')

    def test_property_2_nm_update_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_nm_update_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_property_2_nm_update_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_nm_update_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_property_2_nm.html')

    def test_property_2_m_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_m_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_property_2_m_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_m_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_property_2_m.html')

    def test_property_2_m_update_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_m_update_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_property_2_m_update_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.property_2_m_update_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_property_2_m.html')

    def test_form_add_distribution_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_distribution_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_form_add_distribution_template_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.form_add_distribution_url, follow=True)
        self.assertTemplateUsed(response, 'divorce/form_distribution.html')

    def test_delete_distribution_GET(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.get(self.delete_distribution_url)
        self.assertEquals(response.status_code, 302)

    def test_signup_GET(self):
        response = self.client.get(self.signup_url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_signup_template_GET(self):
        response = self.client.get(self.signup_url, follow=True)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_form_add_Fiz_l_POST(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.post(self.form_add_fiz_l_url, {
            'name': 'Василий Иванович',
            'date_of_birth': '1977-10-28',
            'sex': 'М',
            'service_user': self.user
        })
        self.assertEquals(response.status_code, 302)
        person = list(Fiz_l.objects.filter(name='Василий Иванович'))
        if self.assertEquals(len(person), 1):
            self.assertEquals(person[0].name, 'Василий Иванович')

    def test_person_update_POST(self):
        self.client.login(username='django_test_user', password='password')
        response_1 = self.client.post(self.form_add_fiz_l_url, {
            'name': 'Василий Иванович',
            'date_of_birth': '1977-10-28',
            'sex': 'М',
            'service_user': self.user
        })

        response_2 = self.client.post(self.person_update_url, {
            'name': 'Иннокентий Иванович',
            'date_of_birth': '1977-10-28',
            'sex': 'М',
            'service_user': self.user
        })
        self.assertEquals(response_2.status_code, 302)
        person = list(Fiz_l.objects.filter(name='Иннокентий Иванович'))
        if self.assertEquals(len(person), 1):
            self.assertEquals(person[0].name, ' Иннокентий Иванович')

    def test_form_add_marriage_POST(self):
        self.client.login(username='django_test_user', password='password')
        response = self.client.post(self.form_add_marriage_url, {
            'date_of_marriage_registration': '2018-4-3',
            'service_user': self.user,
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertEquals(response.status_code, 302)
        marriage = list(Marriage.objects.filter(date_of_marriage_registration=datetime.date(2018, 4, 3)))
        self.assertEquals(len(marriage), 1)

    def test_marriage_update_POST(self):
        self.client.login(username='django_test_user', password='password')
        response_1 = self.client.post(self.form_add_marriage_url, {
            'date_of_marriage_registration': '2018-4-3',
            'service_user': self.user,
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })
        marriage = list(Marriage.objects.filter(date_of_marriage_registration=datetime.date(2018, 4, 3)))

        response_2 = self.client.post(reverse('marriage_update', args=[marriage[0].id]), {
            'date_of_marriage_registration': '2019-2-2',
            'service_user': self.user,
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertEquals(response_2.status_code, 302)
        marriage = list(Marriage.objects.filter(date_of_marriage_registration=datetime.date(2019, 2, 2)))
        self.assertEquals(len(marriage), 1)

    def test_marriage_divorce_POST(self):
        self.client.login(username='django_test_user', password='password')
        response_1 = self.client.post(self.form_add_marriage_url, {
            'date_of_marriage_registration': '2018-4-3',
            'service_user': self.user,
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        response_2 = self.client.post(self.marriage_divorce_url, {
            'date_of_marriage_divorce': '2019-6-10',
            'service_user': self.user,
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertEquals(response_2.status_code, 302)
        marriage = list(Marriage.objects.filter(date_of_marriage_divorce=datetime.date(2019, 6, 10)))
        self.assertEquals(len(marriage), 1)