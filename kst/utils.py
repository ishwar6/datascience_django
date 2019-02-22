from .models import *
from states.models import *
from django.db.models import Q
import random


def chapter_switch(user=None):
    '''This function checks the chapter 
    already assessed by student and then return the next chapter
    for which question are to be given'''
    completed_chapters = []
    list_of_chapters = []

    if user:
        student_record = StudentStatus.objects.filter(user=user)
        for record in student_record:
            completed_chapters.append(record.chapter)
        standard = user.standard
        chapters = Chapter.objects.filter(standard=standard)
        for chapter in chapters:
            list_of_chapters.append(chapter)
        next_chapter = list(set(list_of_chapters) - set(completed_chapters))
        random.shuffle(next_chapter)
        if len(next_chapter) == 0:
            end_assessment(user)
            return -1
        else:
            print('chapter switch returned', next_chapter[0])
            a = next_chapter[0]
            return a


###########################__________ GET UNSOLVED QUESTION___________######################################
def getUnsolvedQuestion(user, state):
    '''
    It takes the state and checks all unsolved 
    question of that state and gives a random question
    from that. IT ALSO SAVES IT IN CURRENT QUESTION
    '''
    questions = AssessmentQuestion.objects.filter(state=state)
    solved = QuestionResponse.objects.filter(question__state=state)
    list_of_all_questions = []
    list_of_solved_questions = []
    for q in solved:
        list_of_solved_questions.append(q.question)
    for a in questions:
        list_of_all_questions.append(a)
    print('In getunsolvedquestion', list_of_solved_questions)
    print('list to do', state, user, list_of_all_questions)
    todo = list(set(list_of_all_questions) - set(list_of_solved_questions))
    random.shuffle(todo)
    print('TODO random question list is', todo)
    if len(todo) != 0:
        question = todo[0]
        current = CurrentQuestion.objects.filter(user=user)
        if current.exists():
            current = current.first()
            current.question = question
            current.save()
            return question
        else:
            CurrentQuestion.objects.create(
                user=user,
                question=question
            )
            return question
    else:
        return -1


def getUnsolvedQLoop(user, chapter, state, node):
    '''It chnges current question of user depending upno which were unsolved by him in
    given state else will go to next state and gives again unsolved questions'''

    question = getUnsolvedQuestion(user, state)
    print(question)
    if question == -1:
        print('In getunsolvedquestionLOOOOP')
        print('Details here are:----', state, user, node)
        state, node = switch_nodes(user, chapter, state, node, 1)
        if node == -1 or node == 6:
            return end_assessment(user)
        else:
            getUnsolvedQLoop(user, state, node)
    print('In loop final getunsolved questionloooop', question)
    return question

    ###########################__________ GET UNSOLVED QUESTION___________######################################
