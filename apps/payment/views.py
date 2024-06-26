from django.shortcuts import render, redirect
from ..core.models import Cart, Purchase, Course
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .utils.main import OrderCompletedMail
import stripe
User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request):
    try:
        in_cart = Cart.objects.filter(student=request.user).select_related('course')
        user_id = request.user.id
        line_items = [
            {'price_data': {
                'currency': 'egp',
                'product_data': {'name': cart_obj.course.name},
                'unit_amount': int(cart_obj.course.final_price)*100,
            },
                'quantity': 1,
            }
            for cart_obj in in_cart
        ]
        in_cart = in_cart.values('course_id')
        courses_ids = [str(obj['course_id']) for obj in in_cart]
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=line_items,
            client_reference_id=user_id,
            metadata={
                    'courses_ids': ','.join(courses_ids)
                },
            mode='payment',
            success_url=request.build_absolute_uri('/') + reverse('payment:payment_success') + '?success=true&session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/') + '?canceled=true',
            
        )
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)})

def payment_success(request):
    session_id = request.GET.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    status = checkout_session.get('payment_status')

    if status == 'paid':
        # Get User
        user_id = int(checkout_session.client_reference_id)
        student = User.objects.get(id=user_id)
        # Get Courses IDs
        course_ids = list(map(int, checkout_session.metadata.get('courses_ids').split(','))) # To Int Missing
        # Remove From Cart
        Cart.objects.filter(student=student).delete()
        # Create Purchase
        for course_id in course_ids:
            course = Course.objects.get(id=course_id)
            Purchase.objects.create(student=student, course=course)
        # Send Email 
        OrderCompletedMail(course_ids=course_ids, student=student).send()
    # Redirect 
    return redirect(reverse_lazy('core:MyCourses'))

def payment_failed(request):
    pass    
