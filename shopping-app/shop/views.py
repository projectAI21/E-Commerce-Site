import json
from django.shortcuts import render,redirect
from django.contrib.messages.storage.cookie import CookieStorage
from django.http import HttpResponse,JsonResponse
from shop.models import *
from django.contrib import messages
from .forms import CustomUserForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth import get_user_model
import logging
import re
User = get_user_model()
logger = logging.getLogger(__name__)

def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'shop/index.html', {"products": products})


def cart_page(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        if cart.exists():
            return render(request, 'shop/cart.html', {'cart': cart})
        else:
            messages.warning(request, "You Don't Have Cart Items ! Add Products To View Your Cart <i class='fa fa-shopping-cart'></i> !")
            return redirect('/')
    else:
        messages.warning(request, "Please Login to View Cart Items <i class='fa fa-shopping-cart'></i> !... If You Don't Have User Account Click On Register <i class='fa fa-user'></i> !")
        return redirect('/')
        
         
    
def remove_cart(request, cid):
    cartitem = Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')

def remove_fav(request, fid):
    favitem=Favourite.objects.get(id=fid)
    favitem.delete()
    return redirect('/fav_view_page')
   
def register(request):
    form=CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration Successfully Completed!')
            return redirect('/login')
    return render(request, 'shop/register.html', {"form": form})

from django.http import JsonResponse
import json
from .models import Product, Cart

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_qty = data['product_qty']
            product_id = data['product_id']
            product_status = Product.objects.get(id=product_id)

            if product_status:
                # Check if the product is already in the cart for the user
                existing_cart_item = Cart.objects.filter(user=request.user, product_id=product_id).first()
                
                if existing_cart_item:
                    # Update the quantity if the product is already in the cart
                    new_quantity = existing_cart_item.product_qty + product_qty

                    if product_status.quantity >= new_quantity:
                        existing_cart_item.product_qty = new_quantity
                        existing_cart_item.save()
                        return JsonResponse({'status': f'Quantity updated to {new_quantity} in Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Stock Not Available for this product!'}, status=200)
                else:
                    # Create a new cart entry if the product is not in the cart
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Stock Not Available for this product!'}, status=200)
            else:
                return JsonResponse({'status': 'Product not found'}, status=404)
        else:
            return JsonResponse({'status': 'Login to Add Product to Cart !'}, status=401)
    else:
        return JsonResponse({'status': 'Invalid request'}, status=400)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(password)
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                messages.success(request, "You logged in successfully <i class='fa fa-check fa-md'></i>")
                return redirect('/')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
                return redirect('login')
        return render(request, 'shop/login.html')

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You're successfully Logged out <i class='fa fa-check fa-md'></i>")
        return redirect('/')
def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.load(request)
            product_id=data['product_id']
            product_status=Product.objects.get(id=product_id)
            if product_status:
                if Favourite.objects.filter(user=request.user.id, product_id=product_id):
                    return JsonResponse({'status': 'Prodcut Already Exist in Favourite !'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status':'Product Added to the favourites'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add to Favourite'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)
def fav_view_page(request):
    if request.user.is_authenticated:
        fav = Favourite.objects.filter(user=request.user)
        if fav.exists():
            return render(request, 'shop/fav.html', {'fav': fav})
        else:
            messages.warning(request, "You Don't Have <i class='fa fa-heart'></i> Favourite Items ! Add Products To View Your Favourites !")
            return redirect('/')
    else:
        messages.warning(request, "Please Login to View <i class='fa fa-heart'></i> Favourite Items !... If You Don't Have User Account Click On Register <i class='fa fa-user'></i> !")
        return redirect('/')

def collections(request):
    catagory = Catagory.objects.filter(status=0)
    return render(request, 'shop/collections.html', {"catagory": catagory})

def collectionsview(request,name):
    if(Catagory.objects.filter(name=name,status=0)):
        products = Product.objects.filter(catagory__name = name)
        return render(request, 'shop/products/index.html', {"products": products,"catagory_name" : name })
    else:
        messages.warning(request, 'No Such Catagory Found!')
        return redirect('collections')
    
def productdetails(request, cname, pname):
    if(Catagory.objects.filter(name=cname, status=0)):
        if(Product.objects.filter(name=pname, status=0)):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, 'shop/products/product_details.html', {"products": products})
        else:
            messages.error(request, "NO SUCH PRODUCT/S FOUND")
            return redirect('collections')
    else:
        messages.WARNING('No Such Catagory Found')
        return redirect('collections')

# Create your views here.
