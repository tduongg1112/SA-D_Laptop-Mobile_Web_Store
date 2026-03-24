from django.db import models


class Item(models.Model):
	name = models.CharField(max_length=255)
	category = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

# Create your models here.
