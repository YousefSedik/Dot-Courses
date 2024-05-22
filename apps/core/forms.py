from django import forms


from django import forms
from .models import Question, Choice

class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['right_answer'].queryset = Choice.objects.filter(question=self.instance)
        else:
            self.fields['right_answer'].queryset = Choice.objects.none()