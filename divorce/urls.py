from django.urls import path
from .views import *
urlpatterns = [
    path('', IndexView.as_view()),
    path("divorce/", DivorceView.as_view()),
    path('divorce/add_person/', add_person, name='add_person'),
    path('divorse/del_person/<int:person_id>/', del_person, name='delete_person'),
    path('divorce/form_fiz_l/', fiz_l_form_add, name='form_add'),
    path('divorce/form_fiz_l/<int:id>/', fiz_l_form_add, name='person_update')
]