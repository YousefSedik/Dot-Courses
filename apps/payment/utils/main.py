import datetime
import os
from pymediainfo import MediaInfo
from django import conf
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from ...core.models import Cart, Purchase, Course
User = get_user_model() 


class OrderCompletedMail:
    def __init__(self, course_ids: list, student: User):
        if not isinstance(student, User):
            raise Exception("student must be an instance of User Model!")
        self.student = student
        self.SUBJECT_NAME = "Order complete! Start learning now."
        self._courses = Course.objects.filter(id__in=course_ids)
        self._header_message = "Your order’s been processed\nYou’re all set to start learning. Ready to jump in?\n"
        self._main_message = '\n-'.join([course.name for course in self._courses])
        self._button_message = ""
        self.message = self._header_message + self._main_message + '\n' + self._button_message
    
    def send(self):
        return send_mail(
            subject=self.SUBJECT_NAME,
            message=self.message,
            from_email="from@example.com",
            recipient_list=[self.student.email],
        )