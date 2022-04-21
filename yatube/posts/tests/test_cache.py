from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.post_cash = Post.objects.create(
            author=cls.user,
            text='Тестируем caсhe',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)


def test_cache_page(self):
    response = self.authorized_client.get(reverse('posts:index')).content
    self.post_cash.delete()
    response_cache = self.authorized_client.get(
        reverse('posts:index')).content
    self.assertEqual(response, response_cache)
    cache.clear()
    response_clear = self.authorized_client.get(
        reverse('posts:index')).content
    self.assertNotEqual(response, response_clear)
