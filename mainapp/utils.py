from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.response import Response
from .models import *


class CartMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)


class ObjectDetailMixin(CartMixin):
    model = None
    template = None
    model_two = None

    def get(self, request, slug, *args, **kwargs):
        obj = get_object_or_404(self.model, slug__iexact=slug)
        obj_recommendation = self.model.objects.all()
        return render(
            request, self.template, context=
            {
                self.model.__name__.lower(): obj,
                'admin_object': obj,
                'detail': True,
                '{}_recommendation'.format(self.model.__name__.lower()): obj_recommendation,
                self.model_two.__name__.lower(): obj,
                'cart': self.cart
            }
        )


class ObjectCreateMixin:
    form_model = None
    template = None

    def get(self, request, *args, **kwargs):
        form = self.form_model()
        return render(request, self.template, context={'form': form})

    def post(self, request, *args, **kwargs):
        bound_form = self.form_model(request.POST, request.FILES)
        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form': bound_form})


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    cart.save()


class ObjectAPIMixin:
    model_serializer = None
    model = None

    def get(self, request, *args, **kwargs):
        queryset = self.model.objects.all()
        serializer = self.model_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

