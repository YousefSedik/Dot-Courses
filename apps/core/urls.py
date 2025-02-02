from django.urls import path
from . import views
from . import AJAX_views
app_name = 'core'

AJAX_urlpatterns = [
    path('add-to-cart/<int:course_id>', AJAX_views.AddToCartView.as_view(), name='AddToCart'),
    path('delete-from-cart/<int:course_id>', AJAX_views.DeleteFromCartView.as_view(), name='DeleteFromCart'),
    path('update-or-add-rate/<int:course_id>/<int:is_new>', AJAX_views.UpdateOrAddRateView.as_view(), name='AddRate'),
    path('correction/<int:course_id>/<int:video_counter>', AJAX_views.CorrectionView.as_view(), name='Correction'),
    path('create-certificate/<slug:course_slug>', AJAX_views.CreateCertificateView.as_view(), name='cerate-certificate'),
    path('search', AJAX_views.SearchView.as_view(), name='search'),
    path('nav-bar-cart', AJAX_views.NavbarCartView.as_view(), name='NavBarCart'),

]

main_urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("cart/", views.CartView.as_view(), name="Cart"),
    path(
        "course/<slug:course_slug>",
        views.AboutCourseView.as_view(),
        name="about_course",
    ),
    path(
        "clear-cart-cookies/",
        views.ClearCartCookiesView.as_view(),
        name="ClearCartCookies",
    ),
    path(
        "course/<slug:course_slug>/<int:video_no>/watch",
        views.VideoView.as_view(),
        name="ViewCourse",
    ),
    path(
        "course/<slug:course_slug>/<int:video_id>/exam",
        views.TestCourseView.as_view(),
        name="TestCourse",
    ),
    path("my-courses", views.MyCoursesView.as_view(), name="MyCourses"),
    path("certificate/<slug:key>", views.certificate_view, name="view-certificate"),
    path("certificates/", views.CertificatedListView.as_view(), name="Certificates"),
]

urlpatterns = main_urlpatterns + AJAX_urlpatterns
