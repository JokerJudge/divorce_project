from django.urls import path
from .views import *
urlpatterns = [
    path('', DivorceView.as_view(), name='main'),
    path('del_person/<int:person_id>/', del_person, name='delete_person'),
    path('form_fiz_l/<int:id>/', FizLFormView.as_view(), name='person_update'),
    path('form_fiz_l/', FizLFormView.as_view(), name='form_add_fiz_l'),
    path('form_marriage/', MarriageFormView.as_view(), name='form_add_marriage'),
    path('del_marriage/<int:marriage_id>/', del_marriage, name='delete_marriage'),
    path('form_marriage/<int:id>/', MarriageFormView.as_view(), name='marriage_update'),
    path('form_marriage_divorce/<int:id>/', MarriageFormDivorceView.as_view(), name='marriage_divorce'),
    path('form_property_1/', PropertyFormView.as_view(), name='form_add_property_1'),
    path('del_property/<int:property_id>/', del_property, name='delete_property'),
    path('form_property_1/<int:id>/', PropertyFormView.as_view(), name='property_update'),
    path('form_property_2_nm/', PropertyForm2nmView.as_view(), name='property_2_nm'),
    path('form_property_2_nm/<int:id>/', PropertyForm2nmView.as_view(), name='property_2_nm_update'),
    path('form_property_2_m/', PropertyForm2mView.as_view(), name='property_2_m'),
    path('form_property_2_m/<int:id>/', PropertyForm2mView.as_view(), name='property_2_m_update'),
    path('form_distribution/', DistributionFormView.as_view(), name='form_add_distribution'),
    path('del_distribution/<int:distribution_id>/', del_distribution, name='delete_distribution'),
    path('<int:property_id>/person_1', DivorceView.as_view(), name='common_to_person_1'),
    path('<int:property_id>/person_2', DivorceView.as_view(), name='common_to_person_2'),
    path('<int:property_id>/after_break_up', DivorceView.as_view(), name='common_to_private_after_break_up'),
]

#path('add_person/', add_person, name='add_person'),
#path('form_fiz_l/', fiz_l_form_add, name='form_add'),