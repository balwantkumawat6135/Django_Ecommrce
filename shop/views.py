from django.shortcuts import render, redirect
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from urllib.parse import urlencode
from .models import Order, OrderItem

# Create your views here.
PRODUCTS = [
    {"id": 1, "name": "Product A", "price": 10000},  # ₹100
    {"id": 2, "name": "Product B", "price": 20000},
    {"id": 3, "name": "Product C", "price": 30000},
]
for p in PRODUCTS:
            p["display_price"] = p["price"] / 100
def home(request):
    orders = Order.objects.filter(is_paid=True).order_by('-created_at')
    return render(request, "home.html", {
        "products": PRODUCTS,
        "orders": orders,
        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
        "payment_success": request.GET.get("paid") == "1",
    })

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    if request.method == "POST":
        items = request.POST

        line_items = []
        selected_items = []

        for p in PRODUCTS:
            try:
                qty = int(items.get(f"qty_{p['id']}", 0))
            except (TypeError, ValueError):
                qty = 0

            if qty > 0:
                selected_items.append(
                    {
                        "product_name": p["name"],
                        "quantity": qty,
                        "price": p["price"],
                    }
                )

                line_items.append({
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": p["name"]},
                        "unit_amount": int(p["price"]),
                    },
                    "quantity": qty,
                })

        if not line_items:
            return JsonResponse({"error": "Please select at least one product"}, status=400)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/",
        )

        order = Order.objects.create(stripe_session_id=session.id)
        for item in selected_items:
            OrderItem.objects.create(
                order=order,
                product_name=item["product_name"],
                quantity=item["quantity"],
                price=item["price"],
            )

        return JsonResponse({"id": session.id})
    return JsonResponse({"error": "Invalid request method"}, status=405)
    
def success(request):
    session_id = request.GET.get("session_id")

    order = Order.objects.filter(stripe_session_id=session_id).first()

    if order and not order.is_paid:
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":
            order.is_paid = True
            order.save()

    query = urlencode({"paid": 1})
    return redirect(f"{reverse('home')}?{query}")
