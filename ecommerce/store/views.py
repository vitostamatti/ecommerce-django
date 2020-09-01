from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime


# Create your views here.
def store(request, *args, **kwargs):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0, "get_needs_shipping": False}
        cartItems = order["get_cart_total"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def cart(request, *args, **kwargs):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()  # reverse querying
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0, "get_needs_shipping": False}
        cartItems = order["get_cart_total"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


def checkout(request, *args, **kwargs):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0, "get_needs_shipping": False}
        cartItems = order["get_cart_total"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/checkout.html", context)


def updateCart(request, *args, **kwargs):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False, status=200)


def processOrder(request, *args, **kwargs):
    data = json.loads(request.body)
    transaction_id = datetime.datetime.now().timestamp()
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data["form"]["total"])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.get_needs_shipping:
            shipping_address, created = ShippingAddress.objects.get_or_create(
                customer=customer,
                order=order,
                address=data["shipping"]["address"],
                city=data["shipping"]["city"],
                state=data["shipping"]["state"],
                zipcode=data["shipping"]["zipcode"],
            )
            shipping_address.save()

    else:
        pass
    return JsonResponse("Payment completed!", safe=False, status=200)