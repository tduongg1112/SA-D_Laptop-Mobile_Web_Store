import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Item


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


def staff_login(request):
	if request.user.is_authenticated:
		return redirect('staff_home')

	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		password = request.POST.get('password', '').strip()
		user = authenticate(request, username=username, password=password)
		if user is not None and user.username == 'staff':
			login(request, user)
			return redirect('staff_home')

		messages.error(request, 'Invalid credentials. Use username: staff, password: 123456')

	return render(request, 'staff_core/login.html')


@login_required
def staff_logout(request):
	logout(request)
	return redirect('staff_login')


@login_required
def staff_home(request):
	items_count = Item.objects.count()
	latest_items = Item.objects.order_by('-updated_at')[:6]
	laptop_items = fetch_external_products('laptops')[:3]
	mobile_items = fetch_external_products('mobiles')[:3]
	context = {
		'items_count': items_count,
		'latest_items': latest_items,
		'laptop_items': laptop_items,
		'mobile_items': mobile_items,
	}
	return render(request, 'staff_core/home.html', context)


@login_required
def staff_dashboard(request):
	return redirect('staff_inventory')


@login_required
def staff_inventory(request):
	if request.method == 'POST':
		Item.objects.create(
			name=request.POST.get('name', '').strip(),
			category=request.POST.get('category', '').strip(),
			price=request.POST.get('price', '0'),
			stock=request.POST.get('stock', '0'),
			description=request.POST.get('description', '').strip(),
		)
		messages.success(request, 'New item has been added.')
		return redirect('staff_inventory')

	items = Item.objects.order_by('-updated_at')
	return render(request, 'staff_core/inventory.html', {'items': items})


@login_required
def staff_catalog(request, category):
	if category not in ('laptops', 'mobiles'):
		return redirect('staff_home')
	query = request.GET.get('q', '').strip()
	products = fetch_external_products(category, query=query)
	context = {
		'category': category,
		'products': products,
		'query': query,
	}
	return render(request, 'staff_core/catalog.html', context)


@login_required
def update_item(request, item_id):
	item = get_object_or_404(Item, id=item_id)
	if request.method == 'POST':
		item.name = request.POST.get('name', item.name)
		item.category = request.POST.get('category', item.category)
		item.price = request.POST.get('price', item.price)
		item.stock = request.POST.get('stock', item.stock)
		item.description = request.POST.get('description', item.description)
		item.save()
		messages.success(request, f'Item #{item.id} was updated.')
		return redirect('staff_inventory')

	return render(request, 'staff_core/update_item.html', {'item': item})


@login_required
def delete_item(request, item_id):
	if request.method != 'POST':
		return redirect('staff_inventory')

	item = get_object_or_404(Item, id=item_id)
	item_name = item.name
	item.delete()
	messages.success(request, f'Item {item_name} was deleted.')
	return redirect('staff_inventory')
