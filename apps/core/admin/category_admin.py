from .base_admin import BaseAdmin 
from django.contrib import admin
from ..models import Category

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    pass