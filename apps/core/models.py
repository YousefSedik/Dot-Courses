from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
        
    def __str__(self):
        return f'{self.user} have {self.course} in his cart'

class Category(models.Model):
    name = models.CharField(max_length=50)

class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    thumbnail = models.ImageField(null=True, default='default.jpeg/')
    enrolled_counter = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.RestrictedError)
    duration_in_hour = models.SmallIntegerField(default=0)
    rating = models.DecimalField(max_digits=1, decimal_places=1, default=0)
    rating_added = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.slug}'

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    name = models.CharField(max_length=200)
    counter = models.SmallIntegerField(verbose_name="number of the video in the course")

    def __str__(self):
        return f'this video is for {self.course.slug} course'

class Test(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.CharField(max_length=200) 
    right_answer = models.ForeignKey('Choice', on_delete=models.CASCADE, related_name='answer', null=True, blank=True)

    def __str__(self):
        return self.question
    
class Choice(models.Model):
    question =  models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=200)

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
class Purchase(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Rate(models.Model):
    rate = models.CharField(max_length=1) # 1, 2, 3, 4, 5
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.student} Rated {self.course} with {self.rate} out of 5'

    
# Signals 
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

@receiver(post_save, sender=Purchase)
def increment_enrolled_counter(instance, created, *args, **kwargs):
    if created:
        instance.course.enrolled_counter += 1
        instance.course.save()

@receiver(post_delete, sender=Purchase)
def decrement_enrolled_counter(instance, *args, **kwargs):
    instance.course.enrolled_counter -= 1
    instance.course.save()

@receiver(post_save, sender=Rate)
def add_rating(instance, *args, **kwargs):
    # print(instance__course__id)
    # current_rating = Course.objects.filter(id=instance__course__id)
    pass

# Signal To Add the duration 
@receiver(post_save, sender=Video)
def add_duration_signal(instance, *args, **kwargs):
    pass 


@receiver(post_delete, sender=Video)
def add_duration_signal(instance, *args, **kwargs):
    pass
