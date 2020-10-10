import datetime
from django.test import TestCase
from divorce.models import Fiz_l, Marriage, Property, Distribution
from divorce.forms import Fiz_l_form, Marriage_form, Marriage_form_divorce, Property_form, Distribution_form

class TestForms(TestCase):

    def test_clean_fiz_l_date_of_birth_valid(self):
        form = Fiz_l_form(data={
            'name': 'Сергей Петрович',
            'date_of_birth': datetime.date(1950, 3, 5),
            'sex': 'М'
        })

        self.assertTrue(form.is_valid())

    def test_clean_fiz_l_date_of_birth_invalid(self):
        form = Fiz_l_form(data={
            'name': 'Сергей Петрович',
            'date_of_birth': '1899-3-2',
            'sex': 'М'
        })
        self.assertTrue(form.has_error('date_of_birth'))

    def test_clean_marriage_parties_valid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2015-1-1',
            'date_of_marriage_divorce': '2015-4-3',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.is_valid())

    def test_clean_marriage_parties_invalid_lack_of_parties(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2015-1-1',
            'date_of_marriage_divorce': '2015-4-3',
            'parties': [f'{self.fiz_l_1.id}']
        })

        self.assertTrue(form.has_error('parties'))

    def test_clean_marriage_date_of_marriage_divorce_valid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2015-1-1',
            'date_of_marriage_divorce': '2015-4-3',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.is_valid())

    def test_clean_marriage_date_of_marriage_divorce_invalid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2016-1-1',
            'date_of_marriage_divorce': '2015-4-3',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.has_error('date_of_marriage_divorce'))

    def test_clean_marriage_date_of_break_up_valid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2015-1-1',
            'date_of_break_up': '2016-4-2',
            'date_of_marriage_divorce': '2017-4-9',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.is_valid())

    def test_clean_marriage_date_of_break_up_invalid_earlier(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2015-1-1',
            'date_of_break_up': '2014-4-2',
            'date_of_marriage_divorce': '2017-4-9',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.has_error('date_of_break_up'))
        self.assertFalse(form.is_valid())

    def test_clean_marriage_date_of_break_up_invalid_later(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Marriage_form (data={
            'date_of_marriage_registration': '2015-1-1',
            'date_of_break_up': '2018-4-2',
            'date_of_marriage_divorce': '2017-4-9',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.has_error('date_of_break_up'))
        self.assertFalse(form.is_valid())

    def test_clean_marriage_form_divorce_valid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')
        self.marriage_1 = Marriage.objects.create(
            date_of_marriage_registration='2015-1-1',
        )
        self.marriage_1.parties.add(self.fiz_l_1, self.fiz_l_2)

        form = Marriage_form_divorce(data={
            'date_of_break_up': '2016-4-2',
            'date_of_marriage_divorce': '2017-4-9',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.is_valid())

    def test_clean_marriage_form_divorce_invalid_later(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')
        self.marriage_1 = Marriage.objects.create(
            date_of_marriage_registration='2015-1-1',
        )
        self.marriage_1.parties.add(self.fiz_l_1, self.fiz_l_2)

        form = Marriage_form_divorce(data={
            'date_of_break_up': '2018-4-2',
            'date_of_marriage_divorce': '2017-4-9',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })

        self.assertTrue(form.has_error('date_of_break_up'))
        self.assertFalse(form.is_valid())

    def test_clean_property_date_of_purchase_valid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')

        form = Property_form(data={
            'name': 'Test_квартира',
            'type_of_property_form': 'Квартира',
            'date_of_purchase': '2015-3-5',
            'obtaining_person': self.fiz_l_1,
            'price': '4000000',

        })
        self.assertTrue(form.is_valid())

    def test_clean_property_date_of_purchase_invalid_earlier(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')

        form = Property_form(data={
            'name': 'Test_квартира',
            'type_of_property_form': 'Квартира',
            'date_of_purchase': '1878-3-5',
            'obtaining_person': self.fiz_l_1,
            'price': '4000000',

        })
        self.assertTrue(form.has_error('date_of_purchase'))
        self.assertFalse(form.is_valid())

    def test_clean_property_date_of_purchase_invalid_later(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')

        form = Property_form(data={
            'name': 'Test_квартира',
            'type_of_property_form': 'Квартира',
            'date_of_purchase': '2051-3-5',
            'obtaining_person': self.fiz_l_1,
            'price': '4000000',

        })
        self.assertTrue(form.has_error('date_of_purchase'))
        self.assertFalse(form.is_valid())

    def test_clean_distribution_parties_valid(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Distribution_form(data={
            'date_of_distribution': '2020-5-6',
            'parties': [f'{self.fiz_l_1.id}', f'{self.fiz_l_2.id}']
        })
        self.assertTrue(form.is_valid())

    def test_clean_distribution_parties_invalid_lack_of_parties(self):
        self.fiz_l_1 = Fiz_l.objects.create(name='Петр',
                                            date_of_birth='1988-4-2',
                                            sex='М')
        self.fiz_l_2 = Fiz_l.objects.create(name='Анна',
                                            date_of_birth='1990-6-12',
                                            sex='Ж')

        form = Distribution_form(data={
            'date_of_distribution': '2020-5-6',
            'parties': [f'{self.fiz_l_1.id}']
        })

        self.assertTrue(form.has_error('parties'))
        self.assertFalse(form.is_valid())




