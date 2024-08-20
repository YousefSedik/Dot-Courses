from django.db import models
from datetime import timedelta
from random import randint
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
import secrets
import string
from .utils import main

alphabet = string.ascii_letters + string.digits
key_length = 10

User = get_user_model()


class Cart(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} have {self.course} in his cart"


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, default=0
    )
    discount = models.IntegerField(null=True, blank=True)
    thumbnail = models.ImageField(
        null=True, default="default.jpeg/", upload_to="thumbnail/"
    )
    enrolled_counter = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.RestrictedError)
    duration = models.DurationField(default=timedelta)
    rating_sum = models.IntegerField(default=0)
    rating_added_counter = models.IntegerField(default=0)

    @property
    def rate(self):
        if self.rating_added_counter:
            return f"{(self.rating_sum / self.rating_added_counter):.2f}"
        return 5

    @property
    def final_price(self):
        if self.discount is not None:
            return round(self.price * (100 - self.discount) / 100, 2)
        return self.price if self.price is not None else 0

    def is_eligible_to_get_certificate(self, student: User) -> bool:
        grades = Grade.objects.filter(
            student=student, video__course=self, passed=True
        ).select_related("video")
        grade_mp = {grade.video: 1 for grade in grades}
        grades_count = len(grade_mp)

        questions = Question.objects.filter(video__course=self).select_related("video")
        required_videos = len({question.video: 1 for question in questions})
        if required_videos == grades_count:
            return True

        return False

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = self.super_slugify()

        return super().save(*args, **kwargs)

    def super_slugify(self, course_name=None):
        if course_name is None:
            course_name = self.name
        course_name = slugify(course_name)
        if not Course.objects.filter(slug=course_name).exists():
            return course_name
        else:
            return self.super_slugify(course_name + str(randint(0, 9)))

    def __str__(self):
        return f"{self.slug}"


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.FileField(upload_to="videos/")
    name = models.CharField(max_length=200)
    counter = models.SmallIntegerField(verbose_name="number of the video in the course")

    class Meta:
        ordering = ["counter"]
        unique_together = [["course", "counter"]]

    def __str__(self):
        return f"{self.name} is for {self.course.slug} course"


class Question(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    right_answer = models.ForeignKey(
        "Choice",
        on_delete=models.SET_NULL,
        related_name="answer",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.CharField(max_length=200)

    def __str__(self):
        return self.choice


class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    key = models.SlugField(null=False)
    certificate_pdf = models.FileField(upload_to="certificates/", null=True)

    def __str__(self):
        return f"{self.student} have a certificate in this course {self.course}"

    def generate_key(self):
        while True:
            random_key = "".join(secrets.choice(alphabet) for _ in range(key_length))
            if not Certificate.objects.filter(key=random_key).exists():
                self.key = random_key
                break

    def save(self, *args, **kwargs):
        if not self.key:
            self.generate_key()
            pdf = main.CertificatePDF(
                fullname=self.student.full_name,
                instructor_name=self.course.instructor.full_name,
                key=self.key,
                course_name=self.course.name,
            )
            certificate_path = pdf.create()
            self.certificate_pdf.name = certificate_path
        return super(Certificate, self).save(*args, **kwargs)

    class Meta:
        unique_together = [["student", "course"]]


class Purchase(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["student", "course"]]

    @classmethod
    def create_from_cart(cls, student, course_ids):
        try:
            with transaction.atomic():
                purchase_objs = [
                    cls(student=student, course_id=course_id)
                    for course_id in course_ids
                ]
                cls.objects.bulk_create(purchase_objs)
                # clear the cart
                Cart.objects.filter(student=student).delete()
                return True
        except Exception as e:
            print("Transaction failed and rolled back: ", e)
            return False

    def __str__(self):
        return f"{self.student} have bought this course {self.course}"


class Rate(models.Model):
    rate = models.CharField(max_length=1)  # 1, 2, 3, 4, 5
    review_text = models.TextField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["student", "course"]]

    def __str__(self):
        return f"{self.student} Rated {self.course} with {self.rate} out of 5"


class Grade(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    passed = models.BooleanField()
    student = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.full_name}, passed: {self.passed}, on {self.video}"


class InstructorRequest(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


# Signals


@receiver(post_save, sender=Purchase)
def increment_enrolled_counter(instance, created, *args, **kwargs):
    if created:
        instance.course.enrolled_counter += 1
        instance.course.save()


@receiver(post_delete, sender=Purchase)
def decrement_enrolled_counter(instance, *args, **kwargs):
    instance.course.enrolled_counter -= 1
    instance.course.save()


@receiver(pre_save, sender=Rate)
def add_or_update_rating(sender, instance, *args, **kwargs):
    course_obj = instance.course
    if not instance.pk:  # new
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
    video_path = instance.video.path
    video_time = main.get_duration(video_path)
    course_obj = instance.course
    course_obj.duration += video_time
    course_obj.save()


@receiver(post_delete, sender=Video)
def remove_duration_signal(instance, *args, **kwargs):
    video_path = instance.video.path
    video_time = main.get_duration(video_path)
    course_obj = instance.course
    course_obj.duration -= video_time
    course_obj.save()


@receiver(pre_save, sender=Purchase)
def delete_obj_from_cart(instance, *args, **kwargs):
    course_obj = instance.course
    student = instance.student
    Cart.objects.filter(course=course_obj, student=student).delete()
