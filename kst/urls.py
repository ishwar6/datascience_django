from django.conf.urls import include, url
from django.urls import path
from rest_framework import routers

from .views import (

    QuestionList, getNode, result

)


app_name = 'check'

urlpatterns = [

    url("^list/$", QuestionList.as_view(), name='start'),
    url("^result/assessment/$", result, name='result'),
    url("^node/$", getNode),


]
