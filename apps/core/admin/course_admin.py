from .base_admin import BaseAdmin 
from ..models import Course
from django.contrib import admin

@admin.register(Course)
class CourseAdmin(BaseAdmin):
    fields = ['name', 'slug', 'description', 'price', \
        'discount', 'thumbnail', 'category', 'duration','enrolled_counter',]
    readonly_fields = ['enrolled_counter', 'duration', 'slug']
    
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['name']
        return self.readonly_fields
    def save_model(self, request, obj, form, change):
        if obj.pk is not None:
            original_obj = Course.objects.get(pk=obj.pk)
            obj.enrolled_counter = original_obj.enrolled_counter
            obj.duration = original_obj.duration
            obj.slug = original_obj.slug
            obj.name = original_obj.name
        
        if not obj.pk: # add user to obj
            obj.instructor = request.user
            
        super().save_model(request, obj, form, change)  

    def get_queryset(self, request, **kwargs):
        qs = super().get_queryset(request, **kwargs)
        user = request.user
        if not user.is_superuser:
            qs = qs.filter(instructor=user)
        
        return qs
    