from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Cart, CartItem


def fetch_external_products(category, query=''):
	if category == 'laptops':
		url = f"{settings.LAPTOP_SERVICE_URL}/api/laptops/search/"
	else:
		url = f"{settings.MOBILE_SERVICE_URL}/api/mobiles/search/"

	try:
		response = requests.get(url, params={'q': query}, timeout=6)
		if response.ok:
			return response.json().get('results', [])
	except requests.RequestException:
		return []
	return []


def parse_decimal_price(raw_price):
	value = str(raw_price).strip().replace(',', '.')
	try:
		return Decimal(value)
	except (InvalidOperation, ValueError):
		return Decimal('0')


def get_or_create_customer_cart(user):
	carts = Cart.objects.filter(customer=user).order_by('created_at', 'id')
	primary_cart = carts.first()
	if not primary_cart:
		return Cart.objects.create(customer=user)

	extra_carts = list(carts[1:])
	for extra_cart in extra_carts:
		for extra_item in extra_cart.items.all():
			target_item, created = CartItem.objects.get_or_create(
				cart=primary_cart,
				product_type=extra_item.product_type,
				product_id=extra_item.product_id,
				defaults={
					'product_name': extra_item.product_name,
					'price': extra_item.price,
					'quantity': extra_item.quantity,
				},
			)
			if not created:
				target_item.quantity += extra_item.quantity
				target_item.save(update_fields=['quantity'])
		extra_cart.delete()

	return primary_cart


def customer_login(request):
	if request.user.is_authenticated:
		return redirect('customer_home')

	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '').strip()
		user = authenticate(request, username=username, password=password)

		if user is not None and user.username == 'customer':
			login(request, user)
			return redirect('customer_home')

		messages.error(request, 'Invalid credentials. Use username: customer, password: 123456')

	return render(request, 'customer_core/login.html')


@login_required
def customer_logout(request):
	logout(request)
	return redirect('customer_login')


@login_required
def customer_home(request):
	laptop_items = fetch_external_products('laptops')[:6]
	mobile_items = fetch_external_products('mobiles')[:6]
	cart = get_or_create_customer_cart(request.user)
	cart_items = cart.items.all().order_by('-id')
	cart_lines = [
		{
			'item': item,
			'subtotal': item.price * item.quantity,
		}
		for item in cart_items
	]
	cart_total = sum((item.price * item.quantity for item in cart_items), Decimal('0'))
	context = {
		'cart': cart,
		'cart_items': cart_items,
		'cart_lines': cart_lines,
		'cart_total': cart_total,
		'laptop_items': laptop_items,
		'mobile_items': mobile_items,
	}
	return render(request, 'customer_core/home.html', context)


@login_required
def customer_dashboard(request):
	return redirect('customer_home')


@login_required
def customer_catalog(request, category):
	if category not in ('laptops', 'mobiles'):
		return redirect('customer_home')

	query = request.GET.get('q', '').strip()
	products = fetch_external_products(category, query=query)
	cart = get_or_create_customer_cart(request.user)
	return render(
		request,
		'customer_core/catalog.html',
		{
			'category': category,
			'products': products,
			'query': query,
			'cart': cart,
		},
	)


@login_required
def create_cart(request):
	get_or_create_customer_cart(request.user)
	messages.info(request, 'Each customer has one cart only. Your cart is ready.')
	return redirect('customer_home')


@login_required
def add_to_cart(request):
	if request.method != 'POST':
		return redirect('customer_home')

	cart = get_or_create_customer_cart(request.user)
	product_type = request.POST.get('product_type', 'laptop')
	product_id = int(request.POST.get('product_id', '0'))
	product_name = request.POST.get('product_name', 'Unknown')
	price = parse_decimal_price(request.POST.get('price', '0'))
	quantity = max(1, int(request.POST.get('quantity', '1')))

	item, created = CartItem.objects.get_or_create(
		cart=cart,
		product_type=product_type,
		product_id=product_id,
		defaults={
			'product_name': product_name,
			'price': price,
			'quantity': quantity,
		},
	)
	if not created:
		item.quantity += quantity
		item.product_name = product_name
		item.price = price
		item.save(update_fields=['quantity', 'product_name', 'price'])
	messages.success(request, f'Added {product_name} to cart.')
	return_to = request.POST.get('return_to', 'customer_home')
	if return_to == 'catalog_laptops':
		return redirect('customer_catalog', category='laptops')
	if return_to == 'catalog_mobiles':
		return redirect('customer_catalog', category='mobiles')
	return redirect('customer_home')


@login_required
def update_cart_item(request, item_id):
	if request.method != 'POST':
		return redirect('customer_home')

	cart = get_or_create_customer_cart(request.user)
	item = get_object_or_404(CartItem, id=item_id, cart=cart)
	quantity = max(1, int(request.POST.get('quantity', '1')))
	item.quantity = quantity
	item.save(update_fields=['quantity'])
	messages.success(request, f'Updated quantity for {item.product_name}.')
	return redirect('customer_home')


@login_required
def remove_cart_item(request, item_id):
	if request.method != 'POST':
		return redirect('customer_home')

	cart = get_or_create_customer_cart(request.user)
	item = get_object_or_404(CartItem, id=item_id, cart=cart)
	item_name = item.product_name
	item.delete()
	messages.success(request, f'Removed {item_name} from cart.')
	return redirect('customer_home')


@login_required
def checkout_cart(request):
	if request.method != 'POST':
		return redirect('customer_home')

	cart = get_or_create_customer_cart(request.user)
	removed_count = cart.items.count()
	cart.items.all().delete()
	if removed_count:
		messages.success(request, 'Payment successful. Cart has been cleared.')
	else:
		messages.info(request, 'Your cart is empty.')
	return redirect('customer_home')


@login_required
def search_products(request):
	query = request.GET.get('q', '').strip()
	laptop_data = fetch_external_products('laptops', query=query)
	mobile_data = fetch_external_products('mobiles', query=query)

	return JsonResponse({'query': query, 'laptops': laptop_data, 'mobiles': mobile_data})
