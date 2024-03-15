from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import F
from .models import *
from django.db.models import Exists, OuterRef
# Create your views here.


class HomeView(ListView):
    model = Course
    template_name = 'core/home.html'
    context_object_name = 'courses'
    def get(self, request):
        print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR'])
        return super(HomeView, self).get(request)
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owned=Exists(Purchase.objects.filter(student=self.request.user, course=OuterRef('pk')))
            )
        return queryset

 