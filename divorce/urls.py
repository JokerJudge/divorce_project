from django.urls import path
from .views import *
urlpatterns = [
    path('', IndexView.as_view()),
    path("divorce/", DivorceView.as_view()),
    path('divorce/add_person/', add_person, name='add_person'),
    path('divorse/del_person/<int:person_id>/', del_person, name='delete_person')
]