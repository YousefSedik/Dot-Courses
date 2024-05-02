from apps.core import models
import cv2
from apps.core.utils import main
import datetime
from django.contrib.auth import get_user_model
import random
User = get_user_model()
from apps.users.forms import MyCustomSignupForm
def run():
    # make the durations 0 for all courses
    random_mail =  f'maxxd{random.randint(1,100000)}@gmail.com' 
    form = MyCustomSignupForm()
    form.email = random_mail
    form.password1 = 'fajoe2020'
    form.password2 = 'fajoe2020'
    form.full_name = 'HIIIIII'
    inst = form.save()
    print(inst)
    # User.objects.create(email=random_mail, full_name='maxxd')