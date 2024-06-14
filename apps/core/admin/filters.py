from django.contrib.admin import SimpleListFilter
from ..models import Course, Video, Question

class CourseBaseFilter(SimpleListFilter):
    title = 'Course'
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        courses = Course.objects.all()
        if not request.user.is_superuser:
            courses = courses.filter(instructor=request.user)
        
        data = [(c.id, c.name) for c in courses]
        return data

    def queryset(self, request, queryset, filterDict={}):
        queryset = queryset.filter(**filterDict)
        return queryset

class VideosBaseFilter(SimpleListFilter):
    title = 'Video'
    parameter_name = 'video'

    def lookups(self, request, model_admin):
        videos = Video.objects.all()
        if not request.user.is_superuser:
            videos = videos.filter(course__instructor=request.user)
        if 'course' in request.GET:
            videos = videos.filter(course_id=request.GET.get('course'))


        data = [(v.id, v.name) for v in videos]
        return data

    def queryset(self, request, queryset, filterDict={}):
        queryset = queryset.filter(**filterDict)
        return queryset

class QuestionBaseFilter(SimpleListFilter):
    title = 'Question'
    parameter_name = 'question'

    def lookups(self, request, model_admin):
        questions = Question.objects.all()
        if not request.user.is_superuser:
            questions = questions.filter(video__course__instructor=request.user)
        if 'course' in request.GET:
            questions = questions.filter(video__course_id=request.GET.get('course'))
            
        if 'video' in request.GET:
            questions = questions.filter(video_id=request.GET.get('video'))
        data = [(q.id, q.question) for q in questions]
        return data

    def queryset(self, request, queryset, filterDict={}):
        queryset = queryset.filter(**filterDict)
        return queryset

class CertificateCourseFilter(CourseBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'course_id': self.value()})

class ChoiceCourseFilter(CourseBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'question__video__course_id': self.value()})

class ChoiceVideoFilter(VideosBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'question__video_id': self.value()})

class ChoiceQuestionFilter(QuestionBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'question_id': self.value()})

class PurchaseCourseFilter(CourseBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'course_id': self.value()})

class QuestionCourseFilter(CourseBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'video__course_id': self.value()})

class QuestionVideoFilter(VideosBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'video_id': self.value()})

class RateCoursesFilter(CourseBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'course_id': self.value()})

class VideoCourseFilter(CourseBaseFilter):
    def queryset(self, request, queryset):
        return super().queryset(request, queryset, filterDict={'course_id': self.value()})
