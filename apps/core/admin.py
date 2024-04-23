from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Purchase)
admin.site.register(Certificate)
admin.site.register(Cart)
admin.site.register(Rate)