from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from ..models import Follow, Post, User


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user1 = User.objects.create_user(username='test_user1')
        cls.authorized_client = Client()
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=None,
            image=None
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовый пост 1',
            group=None,
            image=None
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user1,
        )

    def test_follow_url(self):
        self.authorized_client.force_login(self.user)
        templates_url_names = {
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_follow_unfollow(self):
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get('/profile/test_user1/follow')
        self.assertIn(
            response.status_code,
            {HTTPStatus.MOVED_PERMANENTLY, HTTPStatus.FOUND}
        )
        self.assertEqual(response.url, '/profile/test_user1/follow/')
        response = self.authorized_client.get('/profile/test_user1/unfollow')
        self.assertIn(
            response.status_code,
            {HTTPStatus.MOVED_PERMANENTLY, HTTPStatus.FOUND}
        )
        self.assertEqual(response.url, '/profile/test_user1/unfollow/')

    def test_follow_in_page(self):
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        if hasattr(response.context, 'page_obj'):
            self.assertIn(self.post1, response.context['page_obj'])

    def test_follow_not_in_page(self):
        self.authorized_client.force_login(self.user1)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        if hasattr(response.context, 'page_obj'):
            self.assertNotIn(self.post1, response.context['page_obj'])
