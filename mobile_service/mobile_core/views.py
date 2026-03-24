from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from .models import Mobile


def mobile_home(request):
	products = Mobile.objects.all().order_by('-id')[:30]
	featured = products[:6]
	return render(request, 'mobile_core/home.html', {'products': products, 'featured': featured})


def mobile_api_page(request):
	query = request.GET.get('q', '').strip()
	products = Mobile.objects.all().order_by('-id')
	if query:
		products = products.filter(Q(name__icontains=query) | Q(brand__icontains=query))
	return render(request, 'mobile_core/api.html', {'products': products[:60], 'query': query})


def search_mobiles(request):
	query = request.GET.get('q', '').strip()
	products = Mobile.objects.all()
	if query:
		products = products.filter(Q(name__icontains=query) | Q(brand__icontains=query))

	data = [
		{
			'id': item.id,
			'name': item.name,
			'brand': item.brand,
			'price': float(item.price),
			'stock': item.stock,
		}
		for item in products[:50]
	]
	return JsonResponse({'results': data})
