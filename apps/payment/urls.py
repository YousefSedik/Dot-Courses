from django.urls import path
from . import views
app_name = 'payment'
urlpatterns = [
    path('checkout/', views.CheckOutView.as_view(), name='Checkout'),
]