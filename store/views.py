from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from store.models import Product, Category, Profile, Favorite, Size, CartItem, Order, OrderItem
from django.contrib import messages
from django.db.models import Q
from store.forms import ChooseSizeForm, ProfileForm
from django.core.mail import send_mail
from .utils import send_telegram_notification


class HomeView(generic.ListView):
    model = Product
    context_object_name = 'products'

    def get_queryset(self):
        category_id = self.request.GET.get('category')
        queryset = Product.objects.filter(Q(category_id=category_id) if category_id else Q())
        for product in queryset:
            if len(product.description) > 40:
                product.description = product.description[:40] + '...'
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['favorited_products'] = Favorite.objects.filter(user=user).values_list('product_id', flat=True)
            context['products_in_cart'] = CartItem.objects.filter(user=user).values_list('product_id', flat=True)
        else:
            context['favorited_products'] = None
            context['products_in_cart'] = None

        context['categories'] =  Category.objects.all()
        context['sizes'] = Size.objects.all()
        context['form'] = ChooseSizeForm()
        return context

class DetailView(generic.DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'store/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['favorited_products'] = Favorite.objects.filter(user=user).values_list('product_id', flat=True)
            context['products_in_cart'] = CartItem.objects.filter(user=user).values_list('product_id', flat=True)
        else:
            context['favorited_products'] = None
            context['products_in_cart'] = None
        context['sizes'] = Size.objects.all()
        context['form'] = ChooseSizeForm()
        return context

def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_authenticated:
        messages.warning(request, 'Чтобы добавлять товары в избранное, войдите в аккаунт.')
        return redirect(request.META.get('HTTP_REFERER', 'base'))
    if request.method == 'POST':
        favorite = Favorite.objects.filter(user=request.user, product=product).first()
        if favorite:
            favorite.delete()
            messages.success(request, 'Товар удален из избранного.')
        else:
            Favorite.objects.create(user=request.user, product=product)
            messages.success(request, 'Товар добавлен в избранное.')
        return redirect(request.META.get('HTTP_REFERER', 'base'))

class FavoriteView(LoginRequiredMixin, generic.ListView):
    model = Favorite
    context_object_name = 'favorite_product'
    template_name = 'store/favorite_list'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Чтобы добавлять товары в избранное, войдите в аккаунт.")
            return redirect(request.META.get('HTTP_REFERER', 'base'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Favorite.objects.filter(user=self.request.user).select_related('product')
        for favorite in queryset:
            if len(favorite.product.description) > 110:
                favorite.product.description = favorite.product.description[:110] + '...'
        return queryset

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not request.user.is_authenticated:
        messages.warning(request, 'Чтобы добавлять товары в корзину, войдите в аккаунт.')
        return redirect(request.META.get('HTTP_REFERER', 'base'))

    if request.method == 'POST':
        form = ChooseSizeForm(request.POST)
        if form.is_valid():
            size = form.cleaned_data['size']
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product, size=size)
            if not created:
                cart_item.delete()
                messages.success(request, 'Товар удален из корзины.')
            else:
                messages.success(request, 'Товар добавлен в корзину.')
        else:
            messages.warning(request, 'Ошибка при выборе размера.')
        return redirect(request.META.get('HTTP_REFERER', 'base'))

def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        cart_item = CartItem.objects.filter(product=product, user=request.user)
        if cart_item:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины.')
    return redirect('cartitem_list')

class CartView(LoginRequiredMixin, generic.ListView):
    model = CartItem
    context_object_name = 'cart'
    template_name = 'store/cart'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Чтобы добавлять товары в корзину, войдите в аккаунт.")
            return redirect(request.META.get('HTTP_REFERER', 'base'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CartItem.objects.filter(user=self.request.user).select_related('product')
        for cart_item in queryset:
            if len(cart_item.product.description) > 110:
                cart_item.product.description = cart_item.product.description[:110] + '...'
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        total_price = sum(item.product.price for item in cart_items)
        context['total_price'] = total_price
        return context

class ProfileView(LoginRequiredMixin, generic.DetailView):
    model = Profile
    template_name = "store/profile.html"

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders"] = Order.objects.filter(receiver_details=self.get_object()).prefetch_related("items")
        return context


class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "store/profile_edit.html"
    success_url = "/profile/"

    def get_object(self):
        return self.request.user.profile

class OrderCreateView(View):
    def get(self, request, *args, **kwargs):
        user_profile = request.user.profile
        return render(request, 'order/order_confirm.html', {'profile': user_profile})

    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        order = Order.objects.create(
            receiver_details=user.profile,
        )

        order_items = [
            OrderItem(order=order, product=item.product, size=item.size) for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        order.total_price = sum(item.product.price for item in order.items.all())
        order.save(update_fields=["total_price"])

        cart_items.delete()

        send_mail(
            subject='Заказ',
            message=f'Ваш заказ {order.order_number} оформлен на сумму {order.total_price}.\n'
                    f'Скоро с вами свяжется курьер для уточнения деталей доставки по номеру '
                    f'{self.request.user.profile.phone_number}. \n'
                    f'Благодарим за то, что выбрали наш магазин!',
            from_email='noreply@example.com',
            recipient_list= [user.email],
            fail_silently=False,
        )
        send_telegram_notification(order.receiver_details.telegram_user_id, 
            f"Спасибо за заказ!\nНомер заказа: {order.order_number}\nСумма заказа: {order.total_price}\n")

        messages.success(request, f"Ваш заказ оформлен! Доставка будет по адресу: {user.profile.address}")
        return redirect('order_success', order.order_number)

def order_success(request, order_number):
    order = Order.objects.get(order_number=order_number)

    return render(request, 'order/order_success.html', {
        'order': order
    })