from django.db import models


class Mobile(models.Model):
	name = models.CharField(max_length=255)
	brand = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=12, decimal_places=2)
	specs = models.TextField(blank=True)
	stock = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.name

# Create your models here.
