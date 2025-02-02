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
from django.http import JsonResponse
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class SearchView(View):
    def get(self, request, *args, **kwargs):
        q = request.GET.get("q")
        context = {}
        search_vector = SearchVector(
            "name",
            "description",
            "instructor__first_name",
            "instructor__middle_name",
            "instructor__last_name",
        )
        search_query = SearchQuery(q)
        context["courses"] = (
            Course.objects.annotate(rank=SearchRank(search_vector, search_query))
            .filter(rank__gte=0.3)
            .order_by("-rank")
        )

        if self.request.user.is_authenticated:
            context["courses"] = context["courses"].annotate(
                is_owned=Exists(
                    Purchase.objects.filter(
                        student=self.request.user, course=OuterRef("pk")
                    )
                )
            )
        return render(request, "core/components/viewCourse.html", context)


class UpdateOrAddRateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        student = request.user
        course_id = kwargs["course_id"]
        rate_obj = None
        rate = request.POST.get("rate")
        rate_text = request.POST.get("rate_text")
        if not kwargs["is_new"]:
            rate_obj = Rate.objects.filter(course_id=course_id, student=student).first()
            rate_obj.rate = rate
            rate_obj.review_text = rate_text
            rate_obj.save()
            return HttpResponse(
                '<button class="btn btn-primary mb-1 mt-1">Rate Updated Successfully</button>'
            )
        else:
            Rate.objects.create(
                course_id=course_id, student=student, rate=rate, review_text=rate_text
            )

            return HttpResponse(
                '<button class="btn btn-primary mb-1 mt-1">Rate Added Successfully</button>'
            )


class CorrectionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        student = request.user
        video_counter, course_id = kwargs["video_counter"], kwargs["course_id"]
        data = request.POST  # QuestionID -> OptionID
        question_ids = dict(data.lists())
        questions = Question.objects.filter(id__in=question_ids).select_related(
            "right_answer", "video"
        )
        context = {}
        context["Data"] = {}
        correct_answer_counter = 0
        for question in questions:
            if question.right_answer is None:
                raise Exception("Right Answer Should Be Added to the question. ")

            right_answer_id = question.right_answer.id
            chosen_answer_id = data[str(question.id)]

            if right_answer_id == int(chosen_answer_id):
                correct_answer_counter += 1

            context["Data"][question.id] = {
                "right_answer": right_answer_id,
                "chosen_answer": chosen_answer_id,
            }
        # Required_percentage_to_pass = 70%
        percentage = correct_answer_counter / len(questions)
        obj = Grade(video=question.video, student=request.user)
        if percentage >= 0.70:
            obj.passed = True
            context["passed"] = True
            course_slug = get_object_or_404(Course, pk=course_id).slug
            video_counter = video_counter + 1
            next_video = Video.objects.filter(
                course__slug=course_slug, counter=video_counter
            )
            if not next_video.exists():
                video_counter -= 1

            context["next_obj"] = reverse_lazy(
                "core:ViewCourse",
                kwargs={
                    "course_slug": course_slug,
                    "video_no": video_counter,
                },
            )

        else:
            obj.passed = False
            context["passed"] = False

        obj.save()

        # Return as a context question-id -> {real_answer, chosen_answer},
        return render(request, "core/ExamResult.html", context)


class DeleteFromCartView(View):
    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated:  # Remove From DB
            instance = Cart.objects.get(course__id=kwargs["course_id"])
            if instance.student == request.user:
                instance.delete()

        elif request.COOKIES.get("cart"):  # Remove From Cookies

            cookies = request.COOKIES["cart"].split()
            cookies = list(map(int, cookies))
            new_cookies = ""
            for course_id in cookies:
                if course_id == kwargs["course_id"]:
                    continue
                new_cookies += str(course_id) + " "
            response = HttpResponse("")
            response.set_cookie("cart", new_cookies)
            return response

        return HttpResponse("")


class AddToCartView(View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        response = HttpResponse(
            '<a href="{% url "core:Cart" %}" class="btn btn-success w-100 mt-2">Checkout</a>'
        )
        if not request.user.is_authenticated:
            cart_ids = request.COOKIES.get("cart", "")
            list_of_cart_ids = list(map(int, cart_ids.split()))
            if kwargs["course_id"] not in list_of_cart_ids:
                cart_ids += f'{kwargs["course_id"]} '
                response.set_cookie("cart", cart_ids)

        else:
            student = request.user
            if not Purchase.objects.filter(
                course__id=kwargs["course_id"], student=student
            ).exists():
                cart = Cart.objects.create(
                    course_id=kwargs["course_id"], student=student
                )

        return response


class CreateCertificateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # First, check if student is eligible to get the certificate, then create it.
        student = request.user
        course_slug = kwargs["course_slug"]
        course_obj = Course.objects.filter(slug=course_slug).first()
        if course_obj.is_eligible_to_get_certificate(student):
            obj = Certificate.objects.create(course=course_obj, student=student)

            return redirect(
                reverse_lazy("core:view-certificate", kwargs={"key": obj.key})
            )

        else:
            return HttpResponse("Unauthorized", status=401)


class NavbarCartView(View):
    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                cart = Cart.objects.filter(student=request.user).select_related(
                    "course"
                )
                courses = [cart_item.course for cart_item in cart]
            else:
                cart_ids = request.COOKIES.get("cart", "")
                list_of_cart_ids = list(map(int, cart_ids.split())) if cart_ids else []
                courses = Course.objects.filter(id__in=list_of_cart_ids)

            # Convert course objects to dictionaries and extract the image URL
            courses_data = [
                {
                    "name": course.name,
                    "price": int(course.price),
                    "discount": course.discount,
                    "thumbnail": course.thumbnail.url if course.thumbnail else None,
                }
                for course in courses
            ]
            return JsonResponse({"courses": courses_data}, safe=False)
        except Exception as e:
            return JsonResponse({"courses": []}, safe=False)
