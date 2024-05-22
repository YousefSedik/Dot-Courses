from django.contrib import admin
from .models import *
from .forms import QuestionAdminForm

# Register your models here.

admin.site.register(Category)
admin.site.register(Course)

class VideoAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is not None, so this is a change page
            return self.readonly_fields + ['video']
        return self.readonly_fields
    
admin.site.register(Video, VideoAdmin)
admin.site.register(Choice)


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm

admin.site.register(Question, QuestionAdmin)


admin.site.register(Purchase)
admin.site.register(Certificate)
admin.site.register(Cart)
admin.site.register(Rate)
admin.site.register(Grade)