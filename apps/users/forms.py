from django import forms
from allauth.account.forms import SignupForm

class MyCustomSignupForm(SignupForm):
    full_name = forms.CharField(max_length=200)
    def save(self, request):

        user = super(MyCustomSignupForm, self).save(request)
        full_name = self.cleaned_data["full_name"]
        full_name_list = full_name.split(" ")
        for i in range(len(full_name_list)):
            full_name_list[i] = full_name_list[i].strip()

        if len(full_name_list) > 2:
            first_name = full_name_list[0]
            last_name = full_name_list[-1]
            middle_name = " ".join(full_name_list[1:-1])
        elif len(full_name_list) == 2:
            first_name = full_name_list[0]
            last_name = full_name_list[1]
            middle_name = ""
        else:
            first_name = full_name_list[0]
            last_name = ""
            middle_name = ""
        user.first_name = first_name
        user.middle_name = middle_name
        user.last_name = last_name
        
        user.save()
        return user
