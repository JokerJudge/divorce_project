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
]

#path('add_person/', add_person, name='add_person'),
#path('form_fiz_l/', fiz_l_form_add, name='form_add'),