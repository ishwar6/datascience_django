from django.urls import path
from .views import base

app_name = 'kst'

urlpatterns = [

    path('', base, name='base')
]
