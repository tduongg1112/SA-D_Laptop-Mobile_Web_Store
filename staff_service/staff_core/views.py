import json
import requests
from collections import Counter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
	"""Analytics dashboard with charts from product data."""
	laptops = fetch_external_products('laptops')
	mobiles = fetch_external_products('mobiles')
	all_products = laptops + mobiles
	inventory_count = Item.objects.count()

	# Stats
	total_laptops = len(laptops)
	total_mobiles = len(mobiles)
	total_products = total_laptops + total_mobiles

	prices = [float(p.get('price', 0)) for p in all_products]
	stocks = [int(p.get('stock', 0)) for p in all_products]
	total_stock_value = sum(p * s for p, s in zip(prices, stocks))
	avg_price = round(sum(prices) / len(prices), 0) if prices else 0

	# Category distribution
	categories = [p.get('category', 'other') for p in all_products]
	cat_counter = Counter(categories)
	category_labels = list(cat_counter.keys())
	category_values = list(cat_counter.values())

	# Price ranges
	price_ranges = {'< $300': 0, '$300-$600': 0, '$600-$1000': 0, '$1000-$1500': 0, '> $1500': 0}
	for price in prices:
		if price < 300:
			price_ranges['< $300'] += 1
		elif price < 600:
			price_ranges['$300-$600'] += 1
		elif price < 1000:
			price_ranges['$600-$1000'] += 1
		elif price < 1500:
			price_ranges['$1000-$1500'] += 1
		else:
			price_ranges['> $1500'] += 1

	# Brand distribution
	brands = [p.get('brand', 'Unknown') for p in all_products]
	brand_counter = Counter(brands)
	brand_sorted = brand_counter.most_common(8)
	brand_labels = [b[0] for b in brand_sorted]
	brand_values = [b[1] for b in brand_sorted]

	# Stock by type
	laptop_stock = sum(int(p.get('stock', 0)) for p in laptops)
	mobile_stock = sum(int(p.get('stock', 0)) for p in mobiles)

	# Top products
	top_products = sorted(all_products, key=lambda p: float(p.get('price', 0)), reverse=True)[:10]

	context = {
		'total_products': total_products,
		'total_laptops': total_laptops,
		'total_mobiles': total_mobiles,
		'inventory_count': inventory_count,
		'total_stock_value': int(total_stock_value),
		'avg_price': int(avg_price),
		'category_labels': json.dumps(category_labels),
		'category_values': json.dumps(category_values),
		'price_labels': json.dumps(list(price_ranges.keys())),
		'price_values': json.dumps(list(price_ranges.values())),
		'brand_labels': json.dumps(brand_labels),
		'brand_values': json.dumps(brand_values),
		'stock_labels': json.dumps(['Laptops', 'Mobiles']),
		'stock_values': json.dumps([laptop_stock, mobile_stock]),
		'top_products': top_products,
	}
	return render(request, 'staff_core/dashboard.html', context)


@login_required
def staff_customers(request):
	"""Show customer accounts from the customer_db database."""
	import psycopg2
	customers = []
	try:
		conn = psycopg2.connect(
			dbname='customer_db',
			user='postgres',
			password='postgres123',
			host='postgres-db',
			port='5432',
		)
		cur = conn.cursor()
		cur.execute("""
			SELECT id, username, first_name, last_name, email, is_active, date_joined
			FROM auth_user ORDER BY date_joined DESC
		""")
		for row in cur.fetchall():
			customers.append({
				'id': row[0],
				'username': row[1],
				'first_name': row[2],
				'last_name': row[3],
				'email': row[4],
				'is_active': row[5],
				'date_joined': row[6],
			})
		cur.close()
		conn.close()
	except Exception:
		# Fallback: show staff DB users
		from django.contrib.auth.models import User
		customers = list(User.objects.all().order_by('-date_joined').values(
			'id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined'
		))
	return render(request, 'staff_core/customers.html', {'customers': customers})


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
