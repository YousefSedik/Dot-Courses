
from django.contrib.admin import ModelAdmin 


class BaseAdmin(ModelAdmin):
    list_per_page = 25