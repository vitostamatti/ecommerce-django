import json
from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}

    items = []
    order = {"get_cart_total": 0, "get_cart_items": 0, "get_needs_shipping": False}
    cartItems = order["get_cart_total"]

    for i in cart:
        try:
            cartItems += cart[i]["quantity"]
            product = Product.objects.get(id=i)
            total = product.price * cart[i]["quantity"]
            order["get_cart_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "imageUrl": product.imageUrl,
                },
                "quantity": cart[i]["quantity"],
                "get_total": total,
            }
            items.append(item)
            if product.digital == False:
                order["get_needs_shipping"] = True
        except:
            pass
    return {"cartItems": cartItems, "order": order, "items": items}


def cartData(request):
    if request.user.is_authenticated:
        customer, create = Customer.objects.get_or_create(user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cart = cookieCart(request)
        cartItems = cart["cartItems"]
        order = cart["order"]
        items = cart["items"]
    return {"cartItems": cartItems, "order": order, "items": items}


def guestOrder(request, data):
    name = data["form"]["name"]
    email = data["form"]["email"]

    cartData = cookieCart(request)
    cartItems = cartData["cartItems"]
    order = cartData["order"]
    items = cartData["items"]
    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )
    for item in items:
        product = Product.objects.get(id=item["product"]["id"])
        orderItem = OrderItem.objects.create(
            product=product, order=order, quantity=item["quantity"]
        )
    return customer, order
