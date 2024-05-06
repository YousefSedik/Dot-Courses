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
                is_owned=Exists(Purchase.objects.filter(student=self.request.user, course=OuterRef('pk'))), 
                is_rated=Exists(Rate.objects.filter(student=self.request.user, course=OuterRef('pk'))),
                
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AboutCourseView, self).get_context_data(**kwargs)
        context['content'] = Video.objects.filter(course=kwargs['object']).select_related()
        context['rates'] = Rate.objects.filter(course__slug=self.kwargs['course_slug']).select_related('student')

        if self.request.user.is_authenticated:
            context['rate'] = Rate.objects.filter(course=kwargs['object'], student=self.request.user).first()
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
        if request.user.is_authenticated:
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
        context['video'] = Video.objects.filter(course__slug=course_slug, counter=video_no).first()
        video_duration = context['video'].video
        context['course'] = Course.objects.filter(slug=course_slug).first()
        
        return context

class TestCourseView(LoginRequiredMixin, ListView):
    template_name = 'core/ExamCourse.html'
    context_object_name = 'questions'
    model = Question
    def dispatch(self, request, *args, **kwargs):
        if not Purchase.objects.filter(student=request.user, course__slug=kwargs['course_slug']):
            return redirect(reverse_lazy('core:about_course'), args=[kwargs['course_slug']])
        
        return super(TestCourseView, self).dispatch(request, *args, **kwargs)
    
    def get_queryset(self): # primary data
        course_slug, video_id = self.kwargs['course_slug'], self.kwargs['video_id']
        queryset = Question.objects.filter(video_id=video_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TestCourseView, self).get_context_data(**kwargs)
        context['course_content'] = Video.objects.filter()
        context['course'] = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        grades = Grade.objects.filter(video__id=self.kwargs['video_id'], student=self.request.user)
        context['grade'] = grades.last()
        context['passed'] = grades.filter(passed=True).exists()
        # print
        # Check if there is next video: Exam->video->counter + 1 available?
        if context['passed']:
            next_video = Video.objects.filter(course__slug=self.kwargs['course_slug'],
                                              counter=self.kwargs['video_id']+1)
            # (next_video.exists())
            if next_video.exists():
                context['next_video'] = reverse_lazy('core:ViewCourse', kwargs={
                    "course_slug":context['course'].slug,
                    "video_no":self.kwargs['video_id']+1
                })
                print("AAAAAAAAAAAAA")
            else:
                # Get Certificate
                pass 
        print(context['passed'])
        return context

class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = 'core/MyCourses.html'
    model = Purchase 
    context_object_name = 'courses'
    def get_queryset(self):
        queryset = super(MyCoursesView, self).get_queryset()
        queryset = queryset.filter(student=self.request.user).select_related('course')
        return queryset
    
class SearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        context = {}
        context['courses'] = Course.objects.filter(Q(description__contains=q) | \
                                                   Q(name__contains=q) | \
                                                   Q(instructor__full_name__contains=q))
        if self.request.user.is_authenticated:
            context['courses'] = context['courses'].annotate(
                is_owned=Exists(Purchase.objects.filter(student=self.request.user, course=OuterRef('pk')))
            )
        return render(request, 'core/components/viewCourse.html', context)
    
class CreateCertificateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student = request.user 
        course_slug = request.POST.get('course_slug')
        grades = Grade.objects.filter(course__slug=course_slug, student=student, passed=True)
        # grades = grades.distinct()
        # if len(grades) == :
        
        return redirect(reverse_lazy('core:'))
    def get(self, request, *args, **kwargs):
        # Show Certificate
        
        pass 