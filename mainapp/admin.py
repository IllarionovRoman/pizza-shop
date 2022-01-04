from django.contrib import admin
from .models import *

admin.site.register(Products)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)

