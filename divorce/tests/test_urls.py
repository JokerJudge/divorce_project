from django.test import SimpleTestCase
from django.urls import reverse, resolve
from divorce.views import DivorceView, del_person, FizLFormView, MarriageFormView, del_marriage, MarriageFormDivorceView,\
    PropertyFormView, del_property, PropertyForm2nmView, PropertyForm2mView, DistributionFormView, del_distribution, SignUpView


class TestUrls(SimpleTestCase):

    def test_main_is_resolved(self):
        url = reverse('main')
        self.assertEquals(resolve(url).func.view_class, DivorceView)

    # если аргументы обязательны - нужно указать в параметрах reverse необходимые аргумент (например, любой int)
    def test_delete_person_is_resolved(self):
        url = reverse('delete_person', args=['1'])
        self.assertEquals(resolve(url).func, del_person)

    def test_person_update_is_resolved(self):
        url = reverse('person_update', args=['1'])
        self.assertEquals(resolve(url).func.view_class, FizLFormView)

    def test_form_add_fiz_l_is_resolved(self):
        url = reverse('form_add_fiz_l')
        self.assertEquals(resolve(url).func.view_class, FizLFormView)

    def test_form_add_marriage_is_resolved(self):
        url = reverse('form_add_marriage')
        self.assertEquals(resolve(url).func.view_class, MarriageFormView)

    def test_form_delete_marriage_is_resolved(self):
        url = reverse('delete_marriage', args=['1'])
        self.assertEquals(resolve(url).func, del_marriage)

    def test_marriage_update_is_resolved(self):
        url = reverse('marriage_update', args=['1'])
        self.assertEquals(resolve(url).func.view_class, MarriageFormView)

    def test_marriage_divorce_is_resolved(self):
        url = reverse('marriage_divorce', args=['1'])
        self.assertEquals(resolve(url).func.view_class, MarriageFormDivorceView)

    def test_form_add_property_1_is_resolved(self):
        url = reverse('form_add_property_1')
        self.assertEquals(resolve(url).func.view_class, PropertyFormView)

    def test_delete_property_is_resolved(self):
        url = reverse('delete_property', args=['1'])
        self.assertEquals(resolve(url).func, del_property)

    def test_property_update_is_resolved(self):
        url = reverse('property_update', args=['1'])
        self.assertEquals(resolve(url).func.view_class, PropertyFormView)

    def test_property_2_nm_is_resolved(self):
        url = reverse('property_2_nm')
        self.assertEquals(resolve(url).func.view_class, PropertyForm2nmView)

    def test_property_2_nm_update_is_resolved(self):
        url = reverse('property_2_nm_update', args=['1'])
        self.assertEquals(resolve(url).func.view_class, PropertyForm2nmView)

    def test_property_2_m_is_resolved(self):
        url = reverse('property_2_m')
        self.assertEquals(resolve(url).func.view_class, PropertyForm2mView)

    def test_property_2_m_update_is_resolved(self):
        url = reverse('property_2_m_update', args=['1'])
        self.assertEquals(resolve(url).func.view_class, PropertyForm2mView)

    def test_form_add_distribution_is_resolved(self):
        url = reverse('form_add_distribution')
        self.assertEquals(resolve(url).func.view_class, DistributionFormView)

    def test_delete_distribution_is_resolved(self):
        url = reverse('delete_distribution', args=['1'])
        self.assertEquals(resolve(url).func, del_distribution)

    def test_common_to_person_1_is_resolved(self):
        url = reverse('common_to_person_1', args=['1'])
        self.assertEquals(resolve(url).func.view_class, DivorceView)

    def test_common_to_person_2_is_resolved(self):
        url = reverse('common_to_person_2', args=['1'])
        self.assertEquals(resolve(url).func.view_class, DivorceView)

    def test_common_to_private_after_break_up_is_resolved(self):
        url = reverse('common_to_private_after_break_up', args=['1'])
        self.assertEquals(resolve(url).func.view_class, DivorceView)

    def test_convert_to_dolevaya_is_resolved(self):
        url = reverse('convert_to_dolevaya', args=['1'])
        self.assertEquals(resolve(url).func.view_class, DivorceView)

    def test_signup_is_resolved(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func.view_class, SignUpView)