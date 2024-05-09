from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.urls import reverse_lazy
from .models import *
from .utils import main
from django.db.models import Exists, OuterRef
from django.db.models import Q
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
    
    
class UpdateOrAddRateView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        
        student = request.user
        course_id = kwargs['course_id']
        rate_obj = None
        rate = request.POST.get('rate')
        rate_text = request.POST.get('rate_text')
        if not kwargs['is_new']:
            rate_obj = Rate.objects.filter(course_id=course_id, student=student).first()
            rate_obj.rate = rate
            rate_obj.review_text = rate_text
            rate_obj.save()
            return HttpResponse('<button class="btn btn-primary mb-1 mt-1">Rate Updated Successfully</button>')
        else:
            Rate.objects.create(course_id=course_id, student=student, rate=rate, review_text=rate_text)
        
            return HttpResponse('<button class="btn btn-primary mb-1 mt-1">Rate Added Successfully</button>')
        

class CorrectionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student = request.user
        video_id, course_id = kwargs['video_id'], kwargs['course_id']
        data = request.POST # QuestionID -> OptionID
        question_ids = dict(data.lists())
        questions = Question.objects.filter(id__in=question_ids).select_related('right_answer', 'video')
        context = {}
        context["Data"] = {}
        correct_answer_counter = 0
        for question in questions:
            if question.right_answer is None:
                raise Exception("Right Answer Should Be Added to the question. ")
            
            right_answer_id = question.right_answer.id
            chosen_answer_id = (data[str(question.id)][0])
            
            if right_answer_id == int(chosen_answer_id):
                correct_answer_counter += 1

            context["Data"][question.id] = { "right_answer":right_answer_id,
                                             "chosen_answer":chosen_answer_id }
        # Required_percentage_to_pass = 70%
        percentage = correct_answer_counter / len(questions)
        obj = Grade(video=question.video, student=request.user)
        if percentage >= .70:
            obj.passed=True
            context['passed'] = True
        else:
            obj.passed=False
            context['passed'] = False

        obj.save()
        
        # Return as a context question-id -> {real_answer, chosen_answer},
        return render(request, 'core/ExamResult.html', context)
    

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


class CreateCertificateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # First, check if student is eligible to get the certificate, then create it. 
        student = request.user 
        course_slug = kwargs['course_slug']
        course_obj = Course.objects.filter(slug=course_slug).first()
        if course_obj.is_eligible_to_get_certificate(student):
            obj = main.create_certificate(course_obj, student)
            return redirect(reverse_lazy('core:view-certificate', kwargs={'key':obj.key}))
        else:
            return HttpResponse('Unauthorized', status=401)
        
