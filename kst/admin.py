from django.contrib import admin
from .models import *
from states.models import State


admin.site.register(QuestionResponse)
admin.site.register(AssessmentQuestion)
admin.site.register(StudentStatus)
admin.site.register(ChapterResult)
admin.site.register(CurrentQuestion)
