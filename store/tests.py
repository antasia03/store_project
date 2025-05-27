from http.client import responses
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from store.models import Product, Category, Size, CartItem, Order, Profile, Favorite
from django.conf import settings

class PublicStoreViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            price = 100.00,
            description = 'Test description',
            category=self.category
        )



    def test_home_view(self):
        response = self.client.get(reverse('base'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_list.html')

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/product_detail.html")
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        formatted_price = f"{self.product.price:,.2f}".replace(",", " ").replace(".", ",")
        self.assertContains(response, formatted_price)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse("profile"), follow=True)
        self.assertRedirects(response, "/accounts/login/?next=/profile/")

class AuthenticatedStoreViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username="testuser", password="password")
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            description='Test description',
            category=self.category
        )
        self.size = Size.objects.create(name="M")


    def test_add_to_cart(self):
        response = self.client.post(reverse("add_to_cart", args=[self.product.id]), {"size": self.size.id}, follow=True)
        self.assertTrue(CartItem.objects.filter(product=self.product, user=self.user, size=self.size).exists())
        self.assertEqual(response.status_code, 200)

    def test_remove_from_cart(self):
        cart_item = CartItem.objects.create(product=self.product, user=self.user, size=self.size)
        self.assertTrue(CartItem.objects.filter(id=cart_item.id).exists())
        response = self.client.post(reverse("remove_from_cart", args=[self.product.id]), follow=True)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
        self.assertEqual(response.status_code, 200)


    def test_toggle_favorite(self):
        self.assertFalse(Favorite.objects.filter(user=self.user, product = self.product).exists())
        response = self.client.post(reverse("toggle_favorite", args=[self.product.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Favorite.objects.filter(user=self.user, product=self.product).exists())

        response = self.client.post(reverse("toggle_favorite", args=[self.product.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.login(username="testuser", password="password")
        self.assertFalse(Favorite.objects.filter(user=self.user, product = self.product).exists())

    def test_favorite_view(self):
        Favorite.objects.create(user=self.user, product=self.product)
        response = self.client.get(reverse('product_favorite_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/favorite_list.html")
        self.assertContains(response, self.product.name)

    def test_cart_view(self):
        CartItem.objects.create(product=self.product, user=self.user, size=self.size)
        response = self.client.get(reverse("cartitem_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cartitem_list.html')
        self.assertContains(response, self.product.name)

    def test_profile_view_authenticated(self):
        self.user.profile.name = "Test Name"
        self.user.profile.surname = "Test Surname"
        self.user.profile.birthday = "2000-01-01"
        self.user.profile.address = "Test Address"
        self.user.profile.phone_number = "+1234567890"
        self.user.profile.save()

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/profile.html")
        self.assertContains(response, "Test Name")
        self.assertContains(response, "Test Surname")
        self.assertContains(response, "Test Address")
        self.assertContains(response, "+1234567890")

    def test_profile_update_view(self):
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/profile_edit.html")
        new_data = {
            "name": "Updated Name",
            "surname": "Updated Surname",
            "birthday": "1995-05-05",
            "address": "Updated Address",
            "phone_number": "+9876543210"
        }
        response = self.client.post(reverse("profile_edit"), new_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.name, "Updated Name")
        self.assertEqual(self.user.profile.surname, "Updated Surname")
        self.assertEqual(str(self.user.profile.birthday), "1995-05-05")
        self.assertEqual(self.user.profile.address, "Updated Address")
        self.assertEqual(self.user.profile.phone_number, "+9876543210")

    @patch('store.views.send_mail')
    def test_create_order(self, mock_send_mail):
        self.user.profile.name = "Updated Name"
        self.user.profile.surname = "Updated Surname"
        self.user.profile.address = "Updated Address"
        self.user.profile.phone_number = "+1234567890"
        self.user.profile.birthday = "1995-05-05"
        self.user.profile.save()

        CartItem.objects.create(product=self.product, user=self.user, size=self.size)

        response = self.client.post(reverse("order_create"), follow=True)
        self.assertEqual(response.status_code, 200)
        order = Order.objects.filter(receiver_details=self.user.profile).first()
        self.assertIsNotNone(order)

        mock_send_mail.assert_called_once()
        if mock_send_mail.called:
            args, kwargs = mock_send_mail.call_args
            self.assertEqual(kwargs['subject'], "Заказ")
            self.assertIn(self.user.email, kwargs['recipient_list'])
            self.assertIn(f"Ваш заказ {order.order_number} оформлен", kwargs['message'])
            self.assertIn(f"на сумму {order.total_price}", kwargs['message'])
            self.assertIn(self.user.profile.phone_number, kwargs['message'])
        else:
            print("send_mail was not called.")