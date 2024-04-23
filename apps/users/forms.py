from django import forms
from allauth.account.forms import SignupForm

class MyCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=50)
    def save(self, request):

        user = super(MyCustomSignupForm, self).save(request)
        user.first_name = self.first_name
        user.username = None
        user.save()
        return user
