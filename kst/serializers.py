from rest_framework import serializers
from .models import AssessmentQuestion


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        #fields = '__all__'
        fields = ('id', 'text', 'question_image',
                  'option1', 'option2', 'option3', 'option4',
                  'integer_type', 'single_option', 'integeral_answer'
                  )
