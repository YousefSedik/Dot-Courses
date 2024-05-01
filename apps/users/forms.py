from django import forms
from allauth.account.forms import SignupForm

class MyCustomSignupForm(SignupForm):
    full_name = forms.CharField(max_length=50)
    def save(self, request):

        user = super(MyCustomSignupForm, self).save(request)
        user.full_name = self.full_name
        user.username = None
        user.save()
        return user
