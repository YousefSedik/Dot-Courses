from django.shortcuts import render

# Create your views here.

def edit_profile(request):
    return render(request, 'users/edit_profile.html')