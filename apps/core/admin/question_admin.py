from .base_admin import BaseAdmin 
from ..models import Question, Video, Choice
from django.contrib import admin
from .forms import QuestionAdminForm
from .filters import QuestionCourseFilter, QuestionVideoFilter

class ChoiceInline(admin.TabularInline):
    model = Choice 


@admin.register(Question)
class QuestionAdmin(BaseAdmin):
    form = QuestionAdminForm
    list_display = ['question', 'right_answer']
    list_filter = (QuestionCourseFilter, QuestionVideoFilter)

    inlines = [ChoiceInline]
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update(
            {
                "show_save_and_add_another": False,  # hiding save and add another button
            }
        )
        return super().render_change_form(request, context, add, change, form_url, obj)


    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if user.is_instructor and user.is_staff and not user.is_superuser:
            qs = qs.filter(video__course__instructor=user)
        
        return qs
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "video":
            kwargs["queryset"] = Video.objects.filter(course__instructor=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)