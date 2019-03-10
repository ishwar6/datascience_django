from django.conf.urls import include, url
from rest_framework import routers

from .views import (

    QuestionList, getNode

)


app_name = 'check'

urlpatterns = [

    url("^list/$", QuestionList.as_view()),
    url("^node/$", getNode),

]
