from django.shortcuts import HttpResponseRedirect
from django.views import View
from .utils import *
from .forms import *
from .serializers import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView


class BaseView(CartMixin, View):
    def get(self, request):
        products = Products.objects.all()
        category = Category.objects.all()
        context = {
            'products': products,
            'category': category,
            'cart': self.cart

        }
        return render(request, 'website/base_template.html', context)


def products_list(request):
    products = Products.objects.all()
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'website/index.html', context)


def orders_list(request):
    orders = Order.objects.all()
    context = {
        'orders': orders
    }
    return render(request, 'website/index.html', context)


class OrdersDetail(View):
    def get(self, request, slug):
        order = Order.objects.get(slug__iexact=slug)
        return render(request, 'website/orders_detail.html', context={'order': order})


class OrdersView(View, CartMixin):
    def get(self, request):
        orders = Order.objects.all()
        return render(request, 'website/orders.html', context={'orders': orders})


class ProductsDetail(View, ObjectDetailMixin):
    model = Products
    template = 'website/products_detail.html'
    model_two = Category


class CategoryDetail(View, ObjectDetailMixin):
    model = Products
    template = 'website/category_detail.html'
    model_two = Category


class ProductsCreate(View, ObjectCreateMixin):
    form_model = ProductsForm
    template = 'website/products_create.html'
    raise_exception = True


class CategoryCreate(View, ObjectCreateMixin):
    form_model = CategoryForm
    template = 'website/category_create.html'
    raise_exception = True


def products_detail(request, slug):
    products = Products.objects.get(slug__iexact=slug)
    return render(request, 'website/products_detail.html', context={'products': products})


def orders_detail(request, slug):
    orders = Order.objects.get(slug__iexact=slug)
    return render(request, 'website/orders_detail.html', context={'orders': orders})


class CartView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'website/cart.html', context)


class AddToCartView(CartMixin, View):
    def get(self, request, slug,  *args, **kwargs):
        product = Products.objects.get(slug__iexact=slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, product=product
        )
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):
    def get(self, request, slug, *args, **kwargs):
        product = Products.objects.get(slug__iexact=slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):
    def post(self, request, slug, *args, **kwargs):
        product = Products.objects.get(slug__iexact=slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect('/cart/')


class CheckoutView(CartMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'website/checkout.html', context)


class OrderCreate(CartMixin, View):
    def post(self, request):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')


class ProfileView(CartMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer)
        categories = Category.objects.all()
        return render(request, 'website/profile.html', {'orders': orders, 'cart': self.cart, 'categories': categories})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {
            'form': form
        }
        return render(request, 'website/login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'website/login.html', context={'form': form})


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        context = {
            'form': form
        }
        return render(request, 'website/registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return redirect('/')
        context = {
            'form': form
        }
        return render(request, 'website/registration.html', context)


class ProductsAPIView(ObjectAPIMixin, APIView):
    model_serializer = ProductsSerializer
    model = Products


class CustomerAPIView(ObjectAPIMixin, APIView):
    model_serializer = CustomerSerializer
    model = Customer


class CategoryAPIView(ObjectAPIMixin, APIView):
    model_serializer = CategorySerializer
    model = Category


class CartAPIView(ObjectAPIMixin, APIView):
    model_serializer = CartSerializer
    model = Cart


class CartProductAPIView(ObjectAPIMixin, APIView):
    model_serializer = CartProductSerializer
    model = CartProduct


class OrderAPIView(ObjectAPIMixin, APIView):
    model_serializer = OrderSerializer
    model = Order





