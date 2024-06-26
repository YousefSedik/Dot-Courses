import os 

from apps.core.models import *
from random import randint 
from django.template.defaultfilters import slugify


def run():
    # def super_slugify(course_name, same=True):
    #     # if same:
    #     if not Course.objects.filter(slug=course_name).exists():
    #         return slugify(course_name)
    #     else:
    #         return super_slugify(course_name + str(randint(0,9)))
    # print (super_slugify('database'))
    # print (super_slugify('databasess'))
    user = User.objects.get(email='faisal@gmail.com')
    product_ids = [obj['course_id'] for obj in Cart.objects.filter(student=user).select_related('course').values('course_id')]
    print(product_ids)
    
# create_tmp_folder()