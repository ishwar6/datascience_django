from django.urls import path
from .views import learning

app_name = 'states'

urlpatterns = [
    path('', learning, name='learning')


]
