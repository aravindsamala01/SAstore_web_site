from django.shortcuts import render,redirect, get_object_or_404
from .models import Product ,Order, OrderItem , CartItem

from .forms import CheckoutForm , ProductForm

from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib.admin.views.decorators import staff_member_required

import stripe
from django.conf import settings


def home(request):
    return render(request, 'SAstore/home.html')



from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm, CustomSignupForm

# this combo of login and signup page.
def combined_login_signup_view(request):
    signup_form = CustomSignupForm()
    login_form = CustomLoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if 'username' in request.POST and 'password1' in request.POST:
            signup_form = CustomSignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'login_signup.html', {
                    'signup_form': signup_form,
                    'login_form': login_form,
                    'signup_active': True,
                })
        else:
            login_form = CustomLoginForm(request, data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('home')
            else:
                return render(request, 'login_signup.html', {
                    'signup_form': signup_form,
                    'login_form': login_form,
                    'login_active': True,
                })

    return render(request, 'login_signup.html', {
        'signup_form': signup_form,
        'login_form': login_form,
        'login_active': True,
    })



# Shows the Product list
def product_list(request):
    products = Product.objects.all()
    return render(request, 'SAstore/product_list.html', {'products': products})

# Shows the Product details
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'SAstore/product_detail.html', {'product': product})

# to see all products
def all_products(request):
    products = Product.objects.filter(stock__gt=0)
    return render(request, 'SAstore/products.html', {'products': products})


# To ADD the card details.
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        cart[str(product.id)] = cart.get(str(product.id), 0) + 1
        request.session['cart'] = cart
        return redirect('all_products')
    else:
        return redirect('all_products')

    # Add or update quantity
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    return redirect('cart_view')

# TO View the card items
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total
        })
        
    return render(request, 'SAstore/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

# TO Remove the items from the card
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart

    return redirect('cart_view')

# Updating the cart 
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        product_id = str(product_id)

        if quantity > 0:
            cart[product_id] = quantity
        else:
            cart.pop(product_id, None)

        request.session['cart'] = cart

    return redirect('cart_view')


# this is placing the order.
@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.item_total for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                phone=form.cleaned_data['phone'],
                total_price=total_price,
                status='Pending'
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()

            cart_items.delete()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'SAstore/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })



# To show the Order list
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'SAstore/order_list.html', {'orders': orders})

# login code
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'SAstore/my_orders.html', {'orders': orders})


# Signup code
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')  # or redirect to 'product_list'
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})



# To create the new Admin

@staff_member_required
def admin_dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')

    return render(request, 'admin_dashboard.html', {
        'products': products,
        'orders': orders,
        'form': form,
    })


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Add item_total dynamically
    for item in cart_items:
        item.item_total = item.product.price * item.quantity
    
    total_price = sum(item.item_total for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                phone=form.cleaned_data['phone'],
                total_price=total_price,
                status='Pending'
            )
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()

            cart_items.delete()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'SAstore/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })


# order confirmation page..

@login_required
def order_confirmation_view(request, order_id):
    # order = Order.objects.get(id=order_id, user=request.user)
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})

# views.py
# def order_confirmation(request, order_id):
#     order = Order.objects.get(id=order_id)
#     return render(request, 'order_confirmation.html', {'order': order})


# Payment method..
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def charge(request):
    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=cart.keys())

        total_price = 0
        for product in products:
            quantity = cart[str(product.id)]
            total_price += product.price * quantity

        amount_in_cents = int(total_price * 100)  # Stripe expects cents

        try:
            charge = stripe.Charge.create(
                amount=amount_in_cents,
                currency='usd',
                description='Order Payment',
                source=token,
            )

            # Create Order in DB
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                total_amount=total_price,
                status='Completed',
                stripe_charge_id=charge.id,  # optional, useful for tracking
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                phone_number=request.POST.get('phone_number'),
                address=request.POST.get('address'),
            )

            for product in products:
                quantity = cart[str(product.id)]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

            request.session['cart'] = {}  # clear cart
            return redirect('order_confirmation', order_id=order.id)

        except stripe.error.StripeError:
            return redirect('checkout')
    else:
        return redirect('checkout')
    
    # views.py

# this is to see the history of the orders.
def my_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'SAstore/my_orders.html', {'orders': orders})
    else:
        return redirect('login')  # Redirect to login page if user is not authenticated

