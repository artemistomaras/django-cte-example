from django.db import models
from django_cte import CTEManager


class Store(models.Model):
    name = models.CharField(max_length=120, db_index=True)

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=120, db_index=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class Sale(models.Model):
    objects = CTEManager()
    store = models.ForeignKey('Store', related_name='sales', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', related_name='sales', on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, null=False)
    cost = models.DecimalField(max_digits=30, decimal_places=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False, auto_now_add=True)

    class Meta:
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

    def __str__(self):
        return f'{self.cost} ($)'