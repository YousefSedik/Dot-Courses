from ..models import Video, Course
from .forms import QuestionAdminForm
from .base_admin import BaseAdmin 
from django.contrib import admin
from .filters import VideoCourseFilter


@admin.register(Video)
class VideoAdmin(BaseAdmin):
    readonly_fields = []
    list_display = ['course', 'counter']
    list_filter = (VideoCourseFilter, )
    
    class Media:
        js = ("js/video_admin.js",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['video']
        return self.readonly_fields + ['status', 'master_playlist']

    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if user.is_instructor and user.is_staff and not user.is_superuser:
            qs = qs.filter(course__instructor=user)

        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "course":
            kwargs["queryset"] = Course.objects.filter(instructor=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
