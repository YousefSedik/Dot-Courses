from .models import Course, Cart, Video, Question, Grade, Purchase, Rate, Certificate
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.http import FileResponse, Http404
from django.db.models import Exists, OuterRef, Q
from django.urls import reverse_lazy

# Create your views here.


class HomeView(ListView):
    model = Course
    template_name = "core/home.html"
    context_object_name = "courses"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owned=Exists(
                    Purchase.objects.filter(
                        student=self.request.user, course=OuterRef("pk")
                    )
                )
            )
        return queryset


class CartView(ListView):
    template_name = "core/Cart.html"
    model = Cart
    context_object_name = "courses"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = (
                super(CartView, self)
                .get_queryset()
                .filter(student=self.request.user)
                .values_list("course", flat=True)
            )
            queryset = Course.objects.filter(id__in=queryset).select_related(
                "instructor"
            )

        elif self.request.COOKIES.get("cart"):
            data = self.request.COOKIES.get("cart").split()
            data = set(map(int, data))
            queryset = Course.objects.filter(id__in=data)
            queryset = queryset.select_related("instructor")
        else:
            queryset = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        total_price = 0
        for obj in context["courses"]:
            if obj.price:
                total_price += float(obj.final_price)

        context["total_price"] = total_price
        return context


class AboutCourseView(DetailView):
    model = Course
    template_name = "core/AboutCourse.html"
    context_object_name = "course"
    slug_field = "slug"
    slug_url_kwarg = "course_slug"

    def get_queryset(self):
        queryset = (
            super(AboutCourseView, self).get_queryset().select_related("instructor")
        )

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_owned=Exists(
                    Purchase.objects.filter(
                        student=self.request.user, course=OuterRef("pk")
                    )
                ),
                is_rated=Exists(
                    Rate.objects.filter(
                        student=self.request.user, course=OuterRef("pk")
                    )
                ),
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(AboutCourseView, self).get_context_data(**kwargs)
        context["content"] = Video.objects.filter(
            course=kwargs["object"]
        ).select_related()
        context["rates"] = Rate.objects.filter(
            course__slug=self.kwargs["course_slug"]
        ).select_related("student")[:10]

        if self.request.user.is_authenticated:
            context["rate"] = Rate.objects.filter(
                course=kwargs["object"], student=self.request.user
            ).first()
        return context


class ClearCartCookiesView(View):

    def get(self, request, **kwargs):
        response = HttpResponseRedirect("/")
        if request.user.is_authenticated:
            user = request.user
            cookies = request.COOKIES.get("cart")
            if cookies:
                list_of_course_ids = list(map(int, cookies.split()))
                for course_id in list_of_course_ids:
                    Cart.objects.get_or_create(student=user, course_id=course_id)

                response.delete_cookie("cart")

        return response


class VideoView(LoginRequiredMixin, ListView):
    template_name = "core/ViewCourse.html"
    context_object_name = "course_content"
    model = Video

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not Purchase.objects.filter(
                student=request.user, course__slug=kwargs["course_slug"]
            ):
                return redirect(
                    reverse_lazy("core:about_course", args=[kwargs["course_slug"]])
                )

        return super(VideoView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        course_slug = self.kwargs["course_slug"]
        queryset = (
            super(VideoView, self)
            .get_queryset()
            .filter(course__slug=course_slug)
            .prefetch_related("question_set")
            .all()
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VideoView, self).get_context_data(**kwargs)
        course_slug, video_no = self.kwargs["course_slug"], self.kwargs["video_no"]
        context["video"] = Video.objects.filter(
            course__slug=course_slug, counter=video_no
        ).first()
        context["course"] = Course.objects.get(slug=course_slug)
        has_certificate = Certificate.objects.filter(
            student=self.request.user, course=context["course"]
        ).first()
        if has_certificate:
            context["got_certificate"] = has_certificate
        else:
            context["is_eligible_to_get_certificate"] = context[
                "course"
            ].is_eligible_to_get_certificate(self.request.user)

        return context


class TestCourseView(LoginRequiredMixin, ListView):
    template_name = "core/ExamCourse.html"
    context_object_name = "questions"
    model = Question

    def dispatch(self, request, *args, **kwargs):
        if not Purchase.objects.filter(
            student=request.user, course__slug=kwargs["course_slug"]
        ):
            return redirect(
                reverse_lazy("core:about_course"), args=[kwargs["course_slug"]]
            )

        return super(TestCourseView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):  # primary data
        queryset = (
            Question.objects.filter(video_id=self.kwargs["video_id"])
            .prefetch_related("choice_set")
            .all()
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TestCourseView, self).get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, slug=self.kwargs["course_slug"])
        grades = Grade.objects.filter(
            video__id=self.kwargs["video_id"], student=self.request.user
        )
        context["grade"] = grades.last()
        context["passed"] = grades.filter(passed=True).exists()
        if context["passed"]:
            # Check if there is next video: Exam->video->counter + 1 available?
            video_counter = Video.objects.get(pk=self.kwargs["video_id"]).counter + 1

            next_video = Video.objects.filter(
                course__slug=self.kwargs["course_slug"], counter=video_counter
            )

            if not next_video.exists():
                video_counter -= 1

            context["next_video"] = reverse_lazy(
                "core:ViewCourse",
                kwargs={
                    "course_slug": self.kwargs["course_slug"],
                    "video_no": video_counter,
                },
            )

        return context


class MyCoursesView(LoginRequiredMixin, ListView):
    template_name = "core/MyCourses.html"
    model = Purchase
    context_object_name = "courses"

    def get_queryset(self):
        queryset = super(MyCoursesView, self).get_queryset()
        queryset = queryset.filter(student=self.request.user).select_related("course")
        return queryset


class SearchView(ListView):
    paginate_by = 6

    def get(self, request, *args, **kwargs):
        q = request.GET.get("q")
        context = {}
        context["courses"] = Course.objects.filter(
            Q(description__contains=q)
            | Q(name__contains=q)
            | Q(instructor__full_name__contains=q)
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


def certificate_view(request, key):

    pdf_url = get_object_or_404(Certificate, key=key).certificate_pdf.path
    try:
        return FileResponse(open(pdf_url, "rb"), content_type="application/pdf")
    except FileNotFoundError:
        raise Http404()
