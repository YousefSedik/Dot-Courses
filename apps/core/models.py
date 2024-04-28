from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta
User = get_user_model()

class Cart(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
      
    def __str__(self):
        return f'{self.student} have {self.course} in his cart'

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name 

class Course(models.Model): 
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    thumbnail = models.ImageField(null=True, default='default.jpeg/', upload_to='thumbnail/')
    enrolled_counter = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.RestrictedError)
    duration = models.DurationField(default=timedelta)
    rating_sum = models.IntegerField(default=0)
    rating_added_counter = models.IntegerField(default=0)
    
    @property
    def rate(self):
        if self.rating_added_counter:
            return f'{(self.rating_sum / self.rating_added_counter):.2f}'
        return 0
    
    @property
    def final_price(self):
        if self.discount is not None:
            return f'{(self.price * (100-self.discount)/100):.2f}'
        return 0
    
    def __str__(self):
        return f'{self.slug}'

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    name = models.CharField(max_length=200)
    counter = models.SmallIntegerField(verbose_name="number of the video in the course")
    class Meta:
        ordering = ['counter']

    def __str__(self):
        return f'{self.name} is for {self.course.slug} course'


class Question(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    question = models.CharField(max_length=200) 
    right_answer = models.ForeignKey('Choice', on_delete=models.CASCADE, related_name='answer', null=True, blank=True)

    def __str__(self):
        return self.question
    
class Choice(models.Model):
    question =  models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=200)
    def __str__(self):
        return self.choice

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.student} have a certificate in this course {self.course}"
    
class Purchase(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.student} have bought this course {self.course}"
    
class Rate(models.Model):
    rate = models.CharField(max_length=1) # 1, 2, 3, 4, 5
    review_text = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.student} Rated {self.course} with {self.rate} out of 5'


# Signals 
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save

@receiver(post_save, sender=Purchase)
def increment_enrolled_counter(instance, created, *args, **kwargs):
    if created:
        instance.course.enrolled_counter += 1
        instance.course.save()

@receiver(post_delete, sender=Purchase)
def decrement_enrolled_counter(instance, *args, **kwargs):
    instance.course.enrolled_counter -= 1
    instance.course.save()

# @receiver(post_save, sender=Rate)
# def add_rating(instance, *args, **kwargs):
#     # check if the rate is new or it's just getting updated
#     # print(args, kwargs) 
    
@receiver(pre_save, sender=Rate)
def add_or_update_rating(sender, instance, *args, **kwargs):
    
    course_obj = instance.course
    if not instance.pk: # new 
        course_obj.rating_sum += int(instance.rate)
        course_obj.rating_added_counter += 1
    else:
        original_instance = sender.objects.get(pk=instance.pk)
        course_obj.rating_sum -= int(original_instance.rate)
        course_obj.rating_sum += int(instance.rate)
        
    course_obj.save()   
        
# Signal To Add the duration 
@receiver(post_save, sender=Video)
def add_duration_signal(instance, *args, **kwargs):
    video_duration = instance.video
    # print(dir(video_duration), type(video_duration))


@receiver(post_delete, sender=Video)
def remove_duration_signal(instance, *args, **kwargs):
    pass

@receiver(pre_save, sender=Question)
def add_right_answer(instance, *args, **kwargs):
    # if the right_answer is getting updated then you should make 
    # sure that the Choice.question.id == question.id 
    pass