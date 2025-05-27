from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from store.models import Category, Product, Favorite, CartItem, Order, Profile, Size
from store_api.serializers import CategorySerializer, ProductSerializer
import uuid


class StoreAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name="Одежда")
        self.product = Product.objects.create(
            name="Футболка", price=999.99, description="Хлопковая футболка",
            category=self.category, article=uuid.uuid4()
        )
        self.size = Size.objects.create(name="M")
        self.order_data = {
            'receiver_details': self.user.profile.id,  # профиль создается автоматически
            'total_price': 200.00,
            'items': [
                {
                    'product': self.product.id,
                    'size': self.size.id,
                }
            ]
        }

    def test_get_categories(self):
        response = self.client.get("/store_api/categories/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_without_required_fields(self):
        data = {
            "name": "",
            "price": "",
            "description": "Товар без имени и цены",
            "category": self.category.id
        }
        response = self.client.post("/store_api/products/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_to_favorites(self):
        response = self.client.post("/store_api/favorites/", {"product": self.product.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_to_cart(self):
        response = self.client.post("/store_api/cartitems/", {"product": self.product.id, "size": self.size.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_profile(self):
        response = self.client.get("/store_api/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order(self):
        response = self.client.post('/store_api/orders/', self.order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.receiver_details.user, self.user)
        self.assertEqual(order.total_price, 200.00)
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.size, self.size)
