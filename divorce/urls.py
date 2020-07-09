from django.urls import path
from .views import *
urlpatterns = [
    path('', DivorceView.as_view(), name='main'),
    path('del_person/<int:person_id>/', del_person, name='delete_person'),
    path('form_fiz_l/<int:id>/', FizLFormView.as_view(), name='person_update'),
    path('form_fiz_l/', FizLFormView.as_view(), name='form_add'),
]

#path('add_person/', add_person, name='add_person'),
#path('form_fiz_l/', fiz_l_form_add, name='form_add'),