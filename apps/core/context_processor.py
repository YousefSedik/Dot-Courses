from .models import Cart


def cart_counter(request):
    context = {}
    if request.user.is_authenticated:
        context["cart_counter"] = request.user.cart_set.count()
        cart_set = request.user.cart_set.values_list("course_id", flat=True)
        context["in_cart"] = set(cart_set)
    else:
        in_cart = request.COOKIES.get("cart")
        if in_cart:
            in_cart = set(map(int, in_cart.split()))
            in_cart = set(in_cart)
            context["in_cart"] = in_cart
            context["cart_counter"] = len(in_cart)
        else:
            context["cart_counter"] = 0
    return context
