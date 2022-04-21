from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Post

User = get_user_model()


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User_test_1')
        cls.user_2 = User.objects.create_user(username='User_test_2')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестируем подписки',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client.force_login(self.user_2)

    def test_auth_user_follow(self):
        """Проверяем что пользователь может подписаться на автора"""
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': self.user}))
        follow = Follow.objects.get()
        self.assertEqual(str(self.user), str(follow))

    def test_auth_user_unfollow(self):
        """Проверяем что пользователь может отписаться от автора"""
        Follow.objects.create(user=self.user_2, author=self.user)
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           kwargs={'username': self.user}))
        self.assertEqual(Follow.objects.count(), 0)

    def test_post_views_follow_user(self):
        """Запись появляется в ленте подписки"""
        # Вопрос как сделать assert что ошибка doesnotexist ? Через try/except?
        Follow.objects.create(user=self.user_2, author=self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(response, self.post.text)
        Follow.objects.filter(user=self.user_2).filter(
            author=self.user).delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, self.post.text)
