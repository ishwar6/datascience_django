from django.db import models

from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save,post_save
from django.core.validators import MinValueValidator , MaxValueValidator
import random
import os



def upload_image_path_chapters(instance, filename):
    new_filename = random.randint(1,910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "chapters/{new_filename}/{final_filename}".format(
            new_filename=new_filename,
            final_filename=final_filename
            )


def upload_image_path_content(instance, filename):
    new_filename = random.randint(1,9996666666)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "content/{new_filename}/{final_filename}".format(
            new_filename=new_filename,
            final_filename=final_filename
            )

def upload_image_path_illus(instance, filename):
    new_filename = random.randint(1,9996666666)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "illustrations/{new_filename}/{final_filename}".format(
            new_filename=new_filename,
            final_filename=final_filename
            )

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


CHAPTER_CHOICE = (
('algebra', 'Algebra'),
('calculus', 'Calculas'),
('geometry', 'Simple-Geometry'),
('trigo', 'Trigonometry'),
('cartgeo', 'Cartesian-Geometry'),
('others', 'Others')
)




########################################################## Models are defined from here  ##########################################################################################





class Chapter(models.Model):
    title = models.CharField(max_length = 80, blank = False)
    gaurd = models.CharField(max_length = 120, default = 'others', choices = CHAPTER_CHOICE)
    standard = models.IntegerField( default = '10', blank = False)
    image = models.FileField(upload_to = upload_image_path_chapters, null = True, blank = True)


    class Meta:
        db_table = 'Chapter'
    def __str__(self):
       return self.title






class State(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete = models.CASCADE, blank = True, null = True )
    title   = models.TextField(max_length = 120, blank = False, null = False) 
    assessment = models.BooleanField(default = True, help_text = 'Weather there will be assessment for student at learning time')
    rate  = models.IntegerField(default=2, help_text='Difficulty of the state')
    time  = models.IntegerField(default=5, help_text='approx time needed to solve this state fully')
    tag   = models.CharField( max_length = 40, blank = True, null = True  )


    def __str__(self):
        return self.tag






class Node(models.Model):
    state_node  = models.ManyToManyField(State)
    credit      = models.IntegerField(default = 0)

    def __str__(self):
        return str(",".join(p.tag for p in self.state_node.all()))








class Content(models.Model):
    state   =   models.OneToOneField(State, on_delete=models.CASCADE)
    title   =   models.CharField(max_length=120, blank=False, null=False)
    text    =   models.TextField()
    image   =   models.FileField(upload_to = upload_image_path_content, null = True, blank = True)
    image2  =   models.FileField(upload_to = upload_image_path_content, null = True, blank = True)
    image3  =   models.FileField(upload_to = upload_image_path_content, null = True, blank = True)
    credit  =   models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default='2', blank=False,  help_text= 'Give a number according to difficulty of content between 1 to 5')
    time    =   models.IntegerField(default='6', help_text='Time in minutes')
    tag     =   models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return  str(self.title) + ' -- for the state -- ' + str(self.state)










class Illustration(models.Model):
    content   =   models.ForeignKey(Content, on_delete=models.CASCADE)
    text      =   models.TextField(blank = False, null = False )
    answer    =   models.TextField(blank = True, null = True)
    image     =   models.FileField(upload_to = upload_image_path_illus, null = True, blank = True)
    image2    =   models.FileField(upload_to = upload_image_path_illus, null = True, blank = True)
    credit    =   models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default='2', blank=False, help_text= 'Give a number according to difficulty of illustration between 1 to 5')
    counts    =   models.IntegerField(blank = True, null = True, help_text='Leave it blank')



    def __str__(self):
        return  str(self.text)












########################################################################################################################################################################################################################
def state_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        if not instance.tag:
            print('State is created')
            count   = State.objects.filter(chapter = instance.chapter).count()
            instance.tag = str(count) + ' - ' + str(instance.chapter)
            instance.save()
post_save.connect(state_created_receiver, sender = State)

def illus_created_reciever(sender, instance, *args, **kwargs):
            illust_last  =  Illustration.objects.filter(content = instance.content)
            if illust_last.exists():
                illust_last_count = illust_last.last().counts
                instance.counts   = illust_last_count + 1
            else:
                instance.counts = 1

        
pre_save.connect(illus_created_reciever, sender=Illustration)



