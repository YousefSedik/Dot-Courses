from django import forms
from allauth.account.forms import SignupForm

class MyCustomSignupForm(SignupForm):
    full_name = forms.CharField(max_length=200)
    def save(self, request):

        user = super(MyCustomSignupForm, self).save(request)
        user.full_name = self.cleaned_data['full_name']
        user.save()
        return user
