from .base_admin import BaseAdmin 
from django.contrib import admin
from ..models import Certificate
from .filters import CertificateCourseFilter

@admin.register(Certificate) 
class CertificateAdmin(BaseAdmin):
    list_filter = (CertificateCourseFilter, )
    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if user.is_instructor and user.is_staff and not user.is_superuser:
            qs = qs.filter(instructor=user)
        
        return qs