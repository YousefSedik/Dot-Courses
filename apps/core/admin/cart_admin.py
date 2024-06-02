from .base_admin import BaseAdmin 
from django.contrib import admin
from ..models import Cart

@admin.register(Cart)
class CartAdmin(BaseAdmin):
    pass