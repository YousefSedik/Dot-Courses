import os 


    

    # Step 3 
    # Step 4
    # Step 5 
from apps.core.models import *
from random import randint 
from django.template.defaultfilters import slugify

def run():
    def super_slugify(course_name, same=True):
        # if same:
        if not Course.objects.filter(slug=course_name).exists():
            return slugify(course_name)
        else:
            return super_slugify(course_name + str(randint(0,9)))
    print (super_slugify('database'))
    print (super_slugify('databasess'))
    pass 
    
# create_tmp_folder()