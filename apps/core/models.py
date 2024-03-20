from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    # class Meta:
    #     primary_key = [User, 'Course']
        
    def __str__(self):
        return f'{self.user} have {self.course} in his cart'

class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    thumbnail = models.ImageField(null=True, default='default.jpeg/')
    def __str__(self):
        return f'{self.slug}'

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/')
    def __str__(self):
        return f'this video is for {self.   course.slug} course'

class Test(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    
class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.CharField(max_length=200) 
    right_answer = models.ForeignKey('Choice', on_delete=models.CASCADE, related_name='answer')

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
