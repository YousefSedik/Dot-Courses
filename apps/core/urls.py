from django.urls import path
from . import views
app_name = 'core'

AJAX_urlpatterns = [
    path('AddToCart/<int:course_id>', views.AddToCartView.as_view(), name='AddToCart'),
    path('DeleteFromCart/<int:course_id>', views.DeleteFromCartView.as_view(), name='DeleteFromCart'),
    path('AddRate/<int:course_id>/', views.AddRateView.as_view(), name='AddRate'),
    
]

urlpatterns = [
    
    path('', views.HomeView.as_view(), name='home'),
    path('checkout/', views.CheckOutView.as_view(), name='Checkout'),
    path('cart/', views.CartView.as_view(), name='Cart'),
    path('course/<slug:course_slug>', views.AboutCourseView.as_view(), name='about_course'),
    path('ClearCartCookies/', views.ClearCartCookiesView.as_view(), name='ClearCartCookies'),
    path('course/<slug:course_slug>/<int:video_no>/watch', views.ViewCourseView.as_view(), name='ViewCourse'),
    path('course/<slug:course_slug>/<int:video_id>/exam', views.TestCourseView.as_view(), name='TestCourse'),

] + AJAX_urlpatterns