from django.conf import settings
from django.db import models


class Cart(models.Model):
	customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Cart #{self.id} - {self.customer.username}"


class CartItem(models.Model):
	PRODUCT_TYPE_CHOICES = (
		('laptop', 'Laptop'),
		('mobile', 'Mobile'),
	)

	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
	product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
	product_id = models.IntegerField()
	product_name = models.CharField(max_length=255)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	quantity = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.product_name} x {self.quantity}"

# Create your models here.
