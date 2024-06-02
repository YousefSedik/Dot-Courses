from .base_admin import BaseAdmin 
from ..models import Choice, Question
from django.contrib import admin
from .filters import ChoiceCourseFilter, ChoiceVideoFilter, ChoiceQuestionFilter

@admin.register(Choice)
class ChoiceAdmin(BaseAdmin):
    list_display = ['question', 'choice']
    list_filter = (ChoiceCourseFilter, ChoiceVideoFilter, ChoiceQuestionFilter)

    
    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if user.is_instructor and user.is_staff and not user.is_superuser:
            qs = qs.filter(question__video__course__instructor=user)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "question":
            kwargs["queryset"] = Question.objects.filter(video__course__instructor=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)