import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings as my_set
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=my_set.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def page_test_context(self, response):
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        post_image = first_object.image
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
                        'posts/group_list.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}):
                        'posts/create_post.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
                        'posts/profile.html',
        }
        cache.clear()
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.page_test_context(response)

    def test_index_page_cache(self):
        """Проверка cache для index."""
        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост new',
            group=self.group,
            image=None
        )
        response = self.authorized_client.get(reverse('posts:index'))
        new_post.delete()
        self.assertIn(bytes(new_post.text, 'utf-8'), response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        test_string = 'Тестовый пост new'
        bytes_string = test_string.encode()
        self.assertNotIn(bytes_string, response.content)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.page_test_context(response)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        first_object = response.context['page_obj'][0]
        post_author = response.context['author']
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_image, self.post.image)

    def test_detail_page_show_correct_context(self):
        """Шаблон detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        first_object = response.context['post']
        post_id = first_object.id
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_id, 1)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_image, self.post.image)

    def test_edit_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        post_id = response.context['post_id']
        self.assertEqual(post_id, self.post.id)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_page(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}),
        ]
        cache.clear()
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(self.post, response.context['page_obj'])

    def test_post_not_in_group(self):
        post_ng = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=None,
            image=None,
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}))
        self.assertNotIn(post_ng, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            id=1,
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,)
        cls.page_len = 13
        test_posts = []
        for i in range(1, cls.page_len):
            test_posts.append(
                Post(
                    author=cls.user,
                    text='Тестовый пост',
                    group=cls.group
                )
            )
        Post.objects.bulk_create(test_posts)

    def page_test_context(self, response):
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_text = first_object.text
        post_group = first_object.group
        self.assertEqual(post_author, self.user)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)

    def test_first_page_contains_ten_records(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}),
        ]
        cache.clear()
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 my_set.POSTS_AMOUNT)
                self.page_test_context(response)

    def test_second_page_contains_last_records(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}),
        ]
        cache.clear()
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 self.page_len - my_set.POSTS_AMOUNT)
                self.page_test_context(response)
