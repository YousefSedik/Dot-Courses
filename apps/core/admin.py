from django.contrib import admin
from .models import *
from .forms import QuestionAdminForm

# Register your models here.

admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Video)
admin.site.register(Choice)



class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm

admin.site.register(Question, QuestionAdmin)


admin.site.register(Purchase)
admin.site.register(Certificate)
admin.site.register(Cart)
admin.site.register(Rate)
admin.site.register(Grade)