from django.test import Client, TestCase
from django.urls import reverse
from ..forms import User


class UserCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'username': 'test_user',
            'email': 'cc@ww.ru',
            'password1': 'testpass999',
            'password2': 'testpass999',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True)
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='test_user',
            ).exists()
        )
        self.assertRedirects(response, reverse('posts:index'))
