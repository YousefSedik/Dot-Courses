from django.contrib.admin import ModelAdmin 
from django.contrib import admin

admin.site.site_header = "dotCourses Admin"
admin.site.site_title = "dotCourses Admin Portal"
admin.site.index_title = "Welcome to dotCourses Portal"


class BaseAdmin(ModelAdmin):
    list_per_page = 25
