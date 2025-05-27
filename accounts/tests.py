from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core import mail

class AccountTests(TestCase):
    def setUp(self):
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        self.invalid_data = {
            'username': '',  # Пропущено обязательное поле username
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
        }


    def test_sign_up_view_get(self):
        """Тестирует доступность страницы регистрации"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/signup.html')

    def test_sign_up_view_post(self):
        """Тестирует успешную регистрацию"""
        response = self.client.post(reverse('signup'), self.valid_data)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertRedirects(response, reverse('base'))

    def test_signup_view_post_missing_required_field(self):
        """Тестирует, что регистрация не проходит, если обязательные поля пустые"""
        response = self.client.post(reverse('signup'), self.invalid_data)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_view_post_valid_data(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('base'))

    def test_login_view_post_invalid_data(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post(reverse('login'), {'username': 'wronguser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_view(self):
        """Тестирует выход"""
        User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('base'))

    def test_password_reset_view_get(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset/password_reset_form.html')

    def test_password_reset_view_post(self):
        User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        response = self.client.post(reverse('password_reset'), {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Сброс пароля', mail.outbox[0].subject)



