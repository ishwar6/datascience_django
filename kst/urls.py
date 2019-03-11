from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from .views import (

    QuestionList, getNode, result, base, change

)


app_name = 'check'

urlpatterns = [

    url("^list/$", QuestionList.as_view(), name='start'),
    url("^result/assessment/$", result, name='result'),
    url("^progress/learning/mapping/change/state/$", change, name='change'),
    url("^node/$", getNode),
    url("^map/$", base, name='map'),


]
