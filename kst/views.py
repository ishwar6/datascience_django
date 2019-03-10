from django.shortcuts import render, redirect
from django.http import JsonResponse
import random

from django.http import Http404
from django.shortcuts import get_list_or_404, render
from .utils import *
from django.db.models import Q
import random
# rest_framework and knox imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from .serializers import AssessmentQuestionSerializer
import datetime


# models import
from .models import AssessmentQuestion, QuestionResponse
from states.models import *


# models import
from .models import AssessmentQuestion, QuestionResponse
from states.models import *


def base(request):
    return render(request, 'kst/base.html')


class QuestionList(generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)

    serializer_class = AssessmentQuestionSerializer

    def get_queryset(self):
        return AssessmentQuestion.objects.all()

    def post(self, request, *args, **kwargs):
        print(request.POST)
        user = request.user
        current_question = CurrentQuestion.objects.filter(user=user)
        if current_question.exists():
            current_question = current_question.first().question
            # Obtaining the state and chapter on the basis of current question present in CurrentQuestion
            state = current_question.state
            chapter = state.chapter

            # checking the student status on previous chapters
            student_status = StudentStatus.objects.filter(
                Q(user=user) & Q(chapter=chapter))
            if student_status.exists():
                student_status = student_status.first()
                # this condition is IMPOSSIBLE
                if student_status.state != state:
                    return Response({
                        'status': False,
                        'detail': 'Your current question is not matching with your current state. This condition is IMPOSSIBLE. Contact ISHWAR JANGID asap'
                    })

            # checking weather the current question is matching or not with passed question id
            if int(current_question.id) == int(request.POST.get('id', None)):
                return Response({
                    'status': False,
                    'detail': "Your POST request passed question ID was incorrect for current active question of this student"
                })

            else:
                # checking the given answer by student is correct or not
                if current_question.integer_type:
                    if int(request.POST.get('int', '3266')) == int(current_question.integeral_answer):
                        print('answer correct')
                        correct = True
                        # correct answer for integral question, move the student in next state of present chapter
                    else:
                        print('Incorrect Answer')
                        correct = False
                elif current_question.single_option:
                    p = int(request.POST.get('rad', 0))
                    a = 1

                    if(current_question.op1):
                        a = 1
                    if(current_question.op2):
                        a = 2
                    if(current_question.op3):
                        a = 3
                    if(current_question.op4):
                        a = 4

                    if(p == a):
                        print('answer correct')
                        correct = True
                        # correct answer for integral question, move the student in next state of present chapter

                    else:
                        print('Incorrect multiple answer')
                        correct = False

                else:

                    p = int(current_question.op1) == int(
                        request.POST.get('op1'))
                    q = int(current_question.op2) == int(
                        request.POST.get('op2'))
                    r = int(current_question.op3) == int(
                        request.POST.get('op3'))
                    s = int(current_question.op4) == int(
                        request.POST.get('op4'))

                    if(p & q & r & s):
                        print('answer correct')
                        correct = True
                        # correct answer for integral question, move the student in next state of present chapter

                    else:
                        print('Incorrect multiple answer')
                        correct = False

                response = QuestionResponse.objects.filter(
                    Q(user=user) & Q(question=current_question))
                if response.exists():
                    old_obj = StudentStatus.objects.filter(
                        user=user).filter(chapter=chapter).first()
                    jump = old_obj.jump

                else:
                    jump = StudentStatus.objects.updateJump(
                        user, chapter, correct)

                    if current_question.integer_type:

                        QuestionResponse.objects.create(
                            user=user,
                            question=current_question,
                            integer_type_submission=request.POST.get('int'),
                            correct=correct,

                        )
                    elif current_question.single_option:
                        QuestionResponse.objects.create(
                            user=user,
                            question=current_question,
                            correct=correct,

                        )
                    else:
                        QuestionResponse.objects.create(
                            user=user,
                            question=current_question,
                            op1=request.POST.get('op1'),
                            op2=request.POST.get('op2'),
                            op3=request.POST.get('op3'),
                            op4=request.POST.get('op4'),
                            correct=correct,

                        )

            # on the basis of jump making student move to next proper node
                print('Current Node is', student_status.node)
                print('value of jump is', jump)
                outer_state, outer_node = switch_nodes(
                    user, chapter, state, student_status.node, jump)
                print('In post final call', outer_state, user, outer_node)
                if outer_state == 6:
                    cq = CurrentQuestion.objects.filter(user=user).first()
                    cq.assess = True
                    cq.save()
                    return JsonResponse({
                        'status': False,
                        'empty': True,
                        'detail': 'Assessment finished'
                    })

                else:
                    question = getUnsolvedQLoop(
                        user, chapter, outer_state, outer_node)
                    if question != 6:
                        print(' Post REQ current question instance', question)
                    qu = AssessmentQuestion.objects.filter(id=question.id)
                    q_list = qu.values()

                    return Response({
                        'question_image': list(q_list),
                        'empty': False
                    })
        else:
            return JsonResponse({
                'status': False,
                'empty': True,
                'detail': 'Assessment not possible with POST. Try GET'
            })

    '''

    GET is designed to serve two purposes :
     1. To give very first question of assessment to student. It selects all chapters, randomize and present a question to student.
     2. If somehow student stops the assignment in middle, GET will give same state as it was earlier

    '''

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:

            cquestion = CurrentQuestion.objects.filter(user=request.user)
            if cquestion.exists():
                if cquestion.first().assess:
                    return redirect('check:result')
                cquestion = cquestion.first().question

                serializer = AssessmentQuestionSerializer(cquestion)
                print('GET ALREADY DONE')
                context = {
                    'currentquestion': cquestion
                }
                return render(request, 'kst/kst.html', context)

            else:
                current_chapter = chapter_switch(request.user)
                if current_chapter:
                    print('current chapter is', current_chapter)
                    state, node = getNodeState(current_chapter, request.user)
                    if state == 6:
                        cq = CurrentQuestion.objects.filter(user=user).first()
                        cq.assess = True
                        cq.save()
                        return Response({
                            'status': False,
                            'detail': 'Congrts, ASSESSMENT finished'
                        })
                    question = getUnsolvedQLoop(
                        request.user, current_chapter, state, node)
                    if question != 6:
                        print(' GET REQ created first current question instance')
                        serializer = AssessmentQuestionSerializer(question)

                        context = {
                            'currentquestion': question
                        }
                        return render(request, 'kst/kst.html', context)

                cq = CurrentQuestion.objects.filter(user=user).first()
                cq.assess = True
                cq.save()

                return Response({
                    'status': False,
                    'detail': 'Congrts, ASSESSMENT finished'
                })
        else:
            return reverse('account:login')


'''
POST DO:

1. TO give answer, check it and store score for student of that question
2. TO Switch chapters if one ends or if one's assessment finishes in middle
3. To switch nodes of a particular chapter

'''


def getNode(request):
    chapter = Chapter.objects.get(id=2)
    a = getNodeState(chapter)
    context = {
        'a': a
    }
    return render(request, 'index.html', context)


def result(request):
    sr1 = random.randint(30, 60)
    sr2 = random.randint(40, 50)
    sr3 = random.randint(50, 70)
    sr4 = random.randint(10, 30)

    r1 = random.randint(10, 40)
    r2 = random.randint(10, 20)
    r3 = random.randint(20, 40)
    r4 = 100-r1-r2-r3

    rr1 = random.randint(40, 50)
    rr2 = random.randint(20, 50)
    rr3 = 100-rr1-rr2

    context = {
        'r1': r1,
        'r2': r2,
        'r3': r3,
        'r4': r4,
        'sr1': sr1,
        'sr2': sr2,
        'sr3': sr3,
        'sr4': sr4,


        'rr1': rr1,
        'rr2': rr2,
        'rr3': rr3,
        'time': datetime.datetime.now()


    }
    return render(request, 'kst/result.html', context)
