from apps.core import models
import cv2
from apps.core.utils import main
import datetime
from django.contrib.auth import get_user_model
import random
User = get_user_model()
from apps.users.forms import MyCustomSignupForm
# def run():
#     # make the durations 0 for all courses
#     pass
from docx import Document
def run():
    
    fullname, instructor_name, key, course_name = "Yousef", "Youssssss", "12212", "database"
    document = Document("CERTIFICATE-TEMPLATE.docx")
    paragraph = document.core_properties
    print(paragraph.text, "ss")