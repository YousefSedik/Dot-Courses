from django.shortcuts import render, redirect, get_object_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, View, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.urls import reverse_lazy
from .models import *
from django.db.models import Exists, OuterRef
# Create your views here.


class HomeView(ListView):
    model = Course
    template_name = 'core/home.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owned=Exists(Purchase.objects.filter(student=self.request.user, course=OuterRef('pk')))
            )
        return queryset
    

class AddToCartView(View):
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        response = HttpResponse(
            '<button href="{% url "core:Checkout" %}" class="btn btn-primary"> Added To Cart.. Checkout </button> '
            )
        if not request.user.is_authenticated:
            cart_ids = request.COOKIES.get('cart', '')
            list_of_cart_ids = list(map(int, cart_ids.split()))
            if kwargs["course_id"] not in list_of_cart_ids:
                cart_ids += f'{kwargs["course_id"]} '
                response.set_cookie('cart', cart_ids)
            
        else:
            course = get_object_or_404(Course, pk=kwargs['course_id'])
            Cart.objects.get_or_create(course=course, user=request.user)
            
        return response

from django.db.models import Sum
class CartView(ListView):
    template_name = 'core/Cart.html'
    model = Cart 
    context_object_name = 'courses'
    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = super(CartView, self).get_queryset().\
                filter(user=self.request.user).values_list('course', flat=True)
            queryset = Course.objects.filter(id__in = queryset).select_related('instructor')
            
        elif self.request.COOKIES.get('cart'):
            data = self.request.COOKIES.get('cart').split()
            data = set(map(int, data))
            queryset = Course.objects.filter(id__in = data)
            queryset = queryset.select_related('instructor')
        else:
            queryset = None
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        total_price = 0 
        for obj in context['courses']:
            if obj.price:
                total_price += obj.price
            
        context['total_price'] = total_price 
        return context
    
    
class DeleteFromCartView(View):
    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated:# Remove From DB 
            instance = Cart.objects.get(course__id=kwargs['course_id'])
            if instance.user == request.user:
                instance.delete()
        
        elif request.COOKIES.get('cart'): # Remove From Cookies 
            
            cookies = request.COOKIES['cart'].split()
            cookies = list(map(int, cookies))
            new_cookies = ''
            for course_id in cookies:
                if course_id == kwargs['course_id']:
                    continue
                new_cookies += str(course_id) + ' '
            response = HttpResponse('')
            response.set_cookie('cart', new_cookies)
            return response
        
        return HttpResponse('')
    
class CheckOutView(LoginRequiredMixin, View):
    pass 

class AboutCourseView(DetailView):
    model = Course
    template_name = 'core/AboutCourse.html'
    context_object_name = 'course'
    slug_field = 'slug'	
    slug_url_kwarg = 'course_slug'	
    
    def get_queryset(self):
        queryset = super(AboutCourseView, self).get_queryset().select_related('instructor')

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owned=Exists(Purchase.objects.filter(student=self.request.user, course=OuterRef('pk')))
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AboutCourseView, self).get_context_data(**kwargs)
        context['content'] = Video.objects.filter(course=kwargs['object']).select_related()
        return context

class ClearCartCookiesView(View):
    
    def get(self, request, **kwargs):
        response = HttpResponseRedirect('/')
        if request.user.is_authenticated:
            user = request.user
            cookies = request.COOKIES.get('cart')
            if cookies:
                list_of_course_ids = list(map(int, cookies.split()))
                for course_id in list_of_course_ids:
                    Cart.objects.get_or_create(user=user, course_id=course_id)
                
                response.delete_cookie('cart')
        
        return response

