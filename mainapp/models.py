from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from PIL import Image
from io import BytesIO

import sys
import uuid


User = get_user_model()


def cropping_photo(self):
    image = self.image
    img = Image.open(image)
    new_img = img.convert('RGB')
    resized_new_img = new_img.resize((450, 300), Image.ANTIALIAS)
    filestream = BytesIO()
    resized_new_img.save(filestream, 'JPEG', quality=90)
    filestream.seek(0)
    name = '{}.{}'.format(*self.image.name.split('.'))
    self.image = InMemoryUploadedFile(
        filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
    )
    return self.image


class Products(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, db_index=True)
    image = models.ImageField(db_index=True)
    categories = models.ManyToManyField('Category', related_name='products')
    slug = models.SlugField(unique=True, default=uuid.uuid1, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products_detail_url', kwargs={'slug': self.slug})

    def get_add_url(self):
        return reverse('add_to_cart_url', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('delete_to_cart_url', kwargs={'slug': self.slug})

    def get_qty_url(self):
        return reverse('change_qty_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.image = cropping_photo(self)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-id']


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return self.title


class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    orders = models.ManyToManyField('Order', related_name='related_order')

    def __str__(self):
        return self.phone


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart',  on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.product.name)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, related_name='related_orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='В ожидании')
    buying_type = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, default=uuid.uuid1, db_index=True)

    def get_absolute_url(self):
        return reverse('orders_detail_url', kwargs={'slug': self.slug})

    def __str__(self):
        return self.address

    class Meta:
        ordering = ['-id']

