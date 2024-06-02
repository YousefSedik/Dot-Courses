from .base_admin import BaseAdmin 
from ..models import Purchase
from django.contrib import admin
from .filters import PurchaseCourseFilter

@admin.register(Purchase)
class PurchaseAdmin(BaseAdmin):
    list_display = ['student', 'course']
    list_filter = (PurchaseCourseFilter, )

    
    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if user.is_instructor and user.is_staff and not user.is_superuser:
            qs = qs.filter(course__instructor=user)
        
        return qs