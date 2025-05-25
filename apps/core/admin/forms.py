from django import forms
from apps.core.models import Question, Choice, Video, Course


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["right_answer"].queryset = Choice.objects.filter(
                question=self.instance
            )
        else:
            self.fields["right_answer"].queryset = Choice.objects.none()
        self.fields["right_answer"].help_text = "press 'Save and continue editing' below to view updated choice list"

class VideoModelForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = "__all__"
