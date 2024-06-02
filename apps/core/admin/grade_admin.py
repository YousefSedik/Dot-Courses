from .base_admin import BaseAdmin 
from django.contrib import admin
from ..models import Grade

@admin.register(Grade)
class GradeAdmin(BaseAdmin):
    pass