from django.shortcuts import render


from django.http import Http404
from django.shortcuts import get_list_or_404, render
from .utils import *
from django.db.models import Q
import random

# models import
from .models import AssessmentQuestion, QuestionResponse
from states.models import *


def base(request):
    return render(request, 'kst/base.html')


# class QuestionList(generics.GenericAPIView):
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     serializer_class = AssessmentQuestionSerializer

#     def get_queryset(self):
#         return AssessmentQuestion.objects.all()

#     def post(self, request, *args, **kwargs):
#         user = request.user
#         current_question = CurrentQuestion.objects.filter(user=user)
#         if current_question.exists():
#             current_question = current_question.first().question
#             # Obtaining the state and chapter on the basis of current question present in CurrentQuestion
#             state = current_question.state
#             chapter = state.chapter

#             # checking the student status on previous chapters
#             student_status = StudentStatus.objects.filter(
#                 Q(user=user) & Q(chapter=chapter))
#             if student_status.exists():
#                 student_status = student_status.first()
#                 # this condition is IMPOSSIBLE
#                 if student_status.state != state:
#                     return Response({
#                         'status': False,
#                         'detail': 'Your current question is not matching with your current state. This condition is IMPOSSIBLE. Contact ISHWAR JANGID asap'
#                     })

#             # checking weather the current question is matching or not with passed question id
#             if int(current_question.id) != int(request.data.get('id', None)):
#                 return Response({
#                     'status': False,
#                     'detail': "Your POST request passed question ID was incorrect for current active question of this student"
#                 })

#             else:
#                 # checking the given answer by student is correct or not
#                 if current_question.integer_type:
#                     if int(request.data.get('int', '3266')) == int(current_question.integeral_answer):
#                         print('answer correct')
#                         correct = True
#                         # correct answer for integral question, move the student in next state of present chapter
#                     else:
#                         print('Incorrect Answer')
#                         correct = False

#                 else:

#                     p = int(current_question.op1) == int(
#                         request.data.get('op1'))
#                     q = int(current_question.op2) == int(
#                         request.data.get('op2'))
#                     r = int(current_question.op3) == int(
#                         request.data.get('op3'))
#                     s = int(current_question.op4) == int(
#                         request.data.get('op4'))

#                     if(p & q & r & s):
#                         print('answer correct')
#                         correct = True
#                         # correct answer for integral question, move the student in next state of present chapter

#                     else:
#                         print('Incorrect multiple answer')
#                         correct = False

#                 response = QuestionResponse.objects.filter(
#                     Q(user=user) & Q(question=current_question))
#                 if response.exists():
#                     old_obj = StudentStatus.objects.filter(
#                         user=user).filter(chapter=chapter).first()
#                     jump = old_obj.jump

#                 else:
#                     jump = StudentStatus.objects.updateJump(
#                         user, chapter, correct)
#                     QuestionResponse.objects.create(
#                         user=user,
#                         question=current_question,
#                         op1=request.data.get('op1'),
#                         op2=request.data.get('op2'),
#                         op3=request.data.get('op3'),
#                         op4=request.data.get('op4'),
#                         integer_type_submission=request.data.get('int'),
#                         correct=correct,

#                     )

#             # on the basis of jump making student move to next proper node
#                 print('Current Node is', student_status.node)
#                 print('value of jump is', jump)
#                 outer_state, outer_node = switch_nodes(
#                     user, chapter, state, student_status.node, jump)
#                 print('In post final call', outer_state, user, outer_node)
#                 if outer_state == 6:
#                     return Response({
#                         'status': False,
#                         'detail': 'Assessment finished'
#                     })

#                 else:
#                     question = getUnsolvedQLoop(
#                         user, chapter, outer_state, outer_node)
#                     if question != 6:
#                         print(' Post REQ current question instance', question)
#                         serializer = AssessmentQuestionSerializer(question)
#                         return Response(serializer.data)
#                         print('GET REQUEST DETAILS',
#                               current_chapter, state, node)
#                     return Response({
#                         'status': False,
#                         'detail': 'Congrts, ASSESSMENT finished'
#                     })
#         else:
#             return Response({
#                 'status': False,
#                 'detail': 'Assessment not possible with POST. Try GET'
#             })

#     '''

#     GET is designed to serve two purposes :
#      1. To give very first question of assessment to student. It selects all chapters, randomize and present a question to student.
#      2. If somehow student stops the assignment in middle, GET will give same state as it was earlier

#     '''

#     def get(self, request, *args, **kwargs):
#         if request.user.is_authenticated:

#             cquestion = CurrentQuestion.objects.filter(user=request.user)
#             if cquestion.exists():
#                 cquestion = cquestion.first().question
#                 serializer = AssessmentQuestionSerializer(cquestion)
#                 print('GET ALREADY DONE')
#                 return Response(serializer.data)

#             else:
#                 current_chapter = chapter_switch(request.user)
#                 if current_chapter:
#                     print('current chapter is', current_chapter)
#                     state, node = getNodeState(current_chapter, request.user)
#                     if state == 6:
#                         return Response({
#                             'status': False,
#                             'detail': 'Congrts, ASSESSMENT finished'
#                         })
#                     question = getUnsolvedQLoop(
#                         request.user, current_chapter, state, node)
#                     if question != 6:
#                         print(' GET REQ created first current question instance')
#                         serializer = AssessmentQuestionSerializer(question)
#                         return Response(serializer.data)
#                     print('GET REQUEST DETAILS', current_chapter, state, node)
#                 return Response({
#                     'status': False,
#                     'detail': 'Congrts, ASSESSMENT finished'
#                 })


# '''
# POST DO:

# 1. TO give answer, check it and store score for student of that question
# 2. TO Switch chapters if one ends or if one's assessment finishes in middle
# 3. To switch nodes of a particular chapter

# '''


# def getNode(request):
#     chapter = Chapter.objects.get(id=2)
#     a = getNodeState(chapter)
#     context = {
#         'a': a
#     }
#     return render(request, 'index.html', context)
