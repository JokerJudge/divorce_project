from django.urls import path
from .views import *
urlpatterns = [
    path('', IndexView.as_view()),
    path("divorce/", DivorceView.as_view())
]