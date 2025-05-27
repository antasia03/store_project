import uuid
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone
from django.core.validators import RegexValidator


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название категории',
    )

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название товара',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    description = models.CharField(
        max_length=500,
        verbose_name='Описание товара',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    article = models.UUIDField(
        verbose_name='Артикул',
        unique=True,
        blank=True,
        default=uuid.uuid4,
    )

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(
        upload_to='notes_images/%Y/%m/%d/',
        verbose_name='Изображение',
        height_field='height',
        width_field='width',
        null=True,
        blank=True,
    )
    height = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.image:
            img = Image.open(self.image)
            if img.height > 1000 or img.width > 1000:
                output_size = (1000, 1000)
                img.thumbnail(output_size)
                img.save(self.image.path, quality=85, optimize=True)

        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50,
        verbose_name='Имя',
    )
    surname = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
    )
    birthday = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    address = models.CharField(
        max_length=500,
        verbose_name='Aдрес',
    )
    phone_number = models.CharField(
        max_length=15,
        verbose_name='Номер телефона',
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Номер телефона должен быть в формате: '+999999999'. Максимальная длина 15 символов."
        )],
    )
    telegram_user_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.surname} {self.name} ({self.user.username})"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorited_by')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        unique_together = ('user', 'product')

class Size(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]

    name = models.CharField(
        verbose_name='Размер',
        max_length=10,
        choices=SIZE_CHOICES,
        unique=True,
    )

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product', 'size')

class Order(models.Model):
    receiver_details = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name="Данные заказчика")
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая цена")
    order_number = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name="Номер заказа")

    def __str__(self):
        return f'Заказ {self.order_number}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.PROTECT, verbose_name="Размер")

    def __str__(self):
        return self.product.name
