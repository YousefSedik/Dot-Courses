from .base_admin import BaseAdmin 

from ..models import Rate
from django.contrib import admin
from .filters import RateCoursesFilter
  
@admin.register(Rate)
class RateAdmin(BaseAdmin):
    list_filter = (RateCoursesFilter, )
    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if user.is_instructor and user.is_staff and not user.is_superuser:
            qs = qs.filter(course__instructor=user)
        
        return qs

