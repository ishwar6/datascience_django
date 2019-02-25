
from django.contrib import admin
from django.urls import path, include


admin.site.site_header = 'Personalized Learning Path through AI techniques'
admin.site.index_title = 'Personalized Learning Path'
admin.site.site_title = 'Personalized Learning Path'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', include('kst.urls')),
    path('states/', include('states.urls')),
    path('u/', include('userstates.urls'))
]
