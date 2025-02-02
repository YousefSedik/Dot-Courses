from django.urls import path
from . import views
app_name = 'payment'
urlpatterns = [
    path("create-checkout-session/", views.create_checkout_session, name="Checkout"),
    path("payment_success/", views.payment_success, name="payment_success"),
    # path("create_subscription/", views.create_subscription, name="create_subscription"),
]
