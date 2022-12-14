from django.test import TestCase, Client
from ..forms import User


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_users_correct_template_auth_client(self):
        """Проверка авторизованного пользователя."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_correct_template_guest_client(self):
        """Проверка неавторизованного пользователя."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
            'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_change_on_login(self):
        """Страница по адресу /auth/password_change/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get('/auth/password_change/', follow=True)
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/')

    def test_urls_redirect_anonymous_change_done_on_login(self):
        """Страница по адресу /auth/password_change/done перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            '/auth/password_change/done/', follow=True
        )
        self.assertRedirects(response,
                             '/auth/login/?next=/auth/password_change/done/')
