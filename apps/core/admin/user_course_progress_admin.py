from ..models import UserCourseProgress
from .base_admin import BaseAdmin
from django.contrib import admin

@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(BaseAdmin):
    pass
