from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, View, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.urls import reverse_lazy
from .models import *
from django.db.models import Exists, OuterRef, Subquery, Count
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
            '<button href="{% url "payment:Checkout" %}" class="btn btn-primary"> Added To Cart.. Checkout </button> '
            )
        if not request.user.is_authenticated:
            cart_ids = request.COOKIES.get('cart', '')
            list_of_cart_ids = list(map(int, cart_ids.split()))
            if kwargs["course_id"] not in list_of_cart_ids:
                cart_ids += f'{kwargs["course_id"]} '
                response.set_cookie('cart', cart_ids)
            
        else:
            course = get_object_or_404(Course, pk=kwargs['course_id'])
            Cart.objects.get_or_create(course=course, student=request.user)
            
        return response

from django.db.models import Sum
class CartView(ListView):
    template_name = 'core/Cart.html'
    model = Cart 
    context_object_name = 'courses'
    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = super(CartView, self).get_queryset()\
                .filter(student=self.request.user).values_list('course', flat=True)
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
            if instance.student == request.user:
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
                    Cart.objects.get_or_create(student=user, course_id=course_id)
                
                response.delete_cookie('cart')
        
        return response

class ViewCourseView(LoginRequiredMixin, ListView):
    template_name = 'core/ViewCourse.html'
    context_object_name = 'course_content'
    model = Video
    def dispatch(self, request, *args, **kwargs):
        if not Purchase.objects.filter(student=request.user, course__slug=kwargs['course_slug']):
            return redirect(reverse_lazy('core:about_course', args=[kwargs['course_slug']]))
        
        return super(ViewCourseView, self).dispatch(request, *args, **kwargs)
    def get_queryset(self):
        course_slug = self.kwargs['course_slug']
        queryset = super(ViewCourseView, self).get_queryset().filter(course__slug=course_slug)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(ViewCourseView, self).get_context_data(**kwargs)
        course_slug, video_no = self.kwargs['course_slug'], self.kwargs['video_no']
        context['video'] = Video.objects.filter(course__slug=course_slug, counter=video_no)[0]
        video_duration = context['video'].video
        context['course'] = Course.objects.filter(slug=course_slug)[0]
        return context

class TestCourseView(LoginRequiredMixin, ListView):
    template_name = 'core/ExamCourse.html'
    context_object_name = 'questions'
    model = Question
    def dispatch(self, request, *args, **kwargs):
        if not Purchase.objects.filter(student=request.user, course__slug=kwargs['course_slug']):
            return redirect(reverse_lazy('core:about_course'), args=[kwargs['course_slug']])
        
        return super(TestCourseView, self).dispatch(request, *args, **kwargs)
    
    def get_queryset(self): #primary data
        course_slug, video_id = self.kwargs['course_slug'], self.kwargs['video_id']
        queryset = Question.objects.filter(video_id=video_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TestCourseView, self).get_context_data(**kwargs)
        # print(context)
        context['course_content'] = Video.objects.filter()
        context['course'] = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        return context


class CorrectionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student = request.user
        video_id, course_id = kwargs['video_id'], kwargs['course_id']
        data = request.POST 
        question_ids = dict(data.lists())
        questions = Question.objects.filter(id__in=question_ids).select_related('right_answer')
        
        # tests = Test.objects.filter(video__id=video_id, video__course__slug=course_slug).first()
        


class AddRateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student = request.user
        course_id = kwargs['course_id']
        course_obj = get_object_or_404(Course, id=course_id)
        Rate.objects.get_or_create(course=course_obj, student=student, \
            rate=request.POST.get('rate'))
        return HttpResponse('Rate Added Successfully')
