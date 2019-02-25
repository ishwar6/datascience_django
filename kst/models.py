import os
import random
from django.db import models

from states.models import *
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
User = get_user_model()


def upload_image_path_questions(instance, filename):
    new_filename = random.randint(1, 9996666666)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(
        new_filename=new_filename, ext=ext)
    return "questions/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


class AssessmentQuestion(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    text = models.TextField()
    question_image = models.FileField(
        upload_to=upload_image_path_questions, null=True, blank=True)

    option1 = models.CharField(blank=True, max_length=2200)
    option2 = models.CharField(blank=True, max_length=2200)
    option3 = models.CharField(blank=True, max_length=2200)
    option4 = models.CharField(blank=True, max_length=2200)

    op1 = models.BooleanField(default=False)
    op2 = models.BooleanField(default=False)
    op3 = models.BooleanField(default=False)
    op4 = models.BooleanField(default=False)

    integer_type = models.BooleanField(default=False)
    single_option = models.BooleanField(default=False)
    integeral_answer = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return self.text


class QuestionResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    op1 = models.BooleanField(default=False)
    op2 = models.BooleanField(default=False)
    op3 = models.BooleanField(default=False)
    op4 = models.BooleanField(default=False)
    integer_type_submission = models.CharField(blank=True, max_length=200)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.question.id) + '  ' + str(self.user) + '  ' + str(self.correct)


''' 
StudentStatus keeps track of students current running state and node of a perticular
chapter. It also keeps track weather previous question was correct or not.

'''


class StudentStatusManager(models.Manager):
    def updateJump(self, user, chapter, correct=False):
        print(chapter)
        obj_row = self.filter(user=user).filter(chapter=chapter).first()
        print(obj_row.jump)
        count = obj_row.jump
        if correct:
            obj_row.jump = count + 1
            obj_row.save()
            return obj_row.jump
        else:
            obj_row.jump = count - 1
            obj_row.save()
            return obj_row.jump


class StudentStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,  blank=True, null=True)
    node = models.ForeignKey(
        Node, on_delete=models.CASCADE, blank=True, null=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE,  blank=True, null=True)
    jump = models.IntegerField(
        default=0, help_text='1 means last question attempted was correct and -1 means incorrect and so on. 0 means null.')
    score = models.IntegerField(
        default=0, help_text='To save score of student from question assessment session')
    empty = models.BooleanField(
        default=False, help_text='Empty true if chapter have no state or no node')

    objects = StudentStatusManager()

    def __str__(self):
        if self.node and self.state:
            return str(self.user) + ' is in ' + str(self.state) + '  >> With active in ' + str(self.node) + ' jump is   ' + str(self.jump)
        else:
            return str(self.user) + 'chapter' + str(self.chapter)

    def clean(self, *args, **kwargs):
        if self.node and self.state:
            valid = 0
            for state in self.node.state_node.all():
                if self.state == state:
                    valid = 1
                    break
            if valid == 0:
                raise ValidationError("State should be within the Node")
            if self.state.chapter != self.chapter:
                raise ValidationError('Chapter and state are not matching')


'''
ChapterResult stores state and node of the student either after
 the assessment or in middle of assessment.

'''


class ChapterResult(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True)
    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE,  blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    node = models.ForeignKey(
        Node, on_delete=models.CASCADE,  blank=True, null=True)
    dont_know_switch = models.BooleanField(default=0)

    def __str__(self):
        return str(self.user) + ' for the node >> ' + str(self.node) + ' << for the chapter ' + str(self.chapter)

    def clean(self, *args, **kwargs):
        valid = 0
        for state in self.node.state_node.all():
            if self.state == state:
                valid = 1
                break
        if valid == 0:
            raise ValidationError("State should be within the Node")
        if self.state.chapter != self.chapter:
            raise ValidationError('Chapter and state are not matching')


'''
CurrentQuestion is UNIQUE and can be only one for a student. It changes continuously 
as the chapter proceeds. It gives current active question of the student. 

'''


class CurrentQuestion(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.DO_NOTHING, blank=True,
                                 null=True, help_text=' Gives current question only if chapter is running currently ')

    def __str__(self):
        return 'For user' + str(self.user) + 'current question is' + str(self.question)

    def get_question(self):
        return self.question
