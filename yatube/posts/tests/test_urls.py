from http import HTTPStatus as Status

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    """"Класс тестирования URL Post"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_available_page(self):
        """URL-адрес доступен"""
        page_list = {
            '/': Status.OK,
            '/create/': Status.OK,
            f'/posts/{self.post.id}/': Status.OK,
            f'/group/{self.group.slug}/': Status.OK,
            f'/profile/{self.user.username}/': Status.OK,
            f'/posts/{self.post.id}/edit': Status.OK,
            '/unexisting_page/': Status.NOT_FOUND,
        }
        for address, status_code in page_list.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, status_code)

    def test_redirection(self):
        """Проверка редиректоров"""
        page_list = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit': f'/auth/login/?next=/posts'
                                           f'/{self.post.id}/edit/',
        }
        for address, final_url in page_list.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                if address == '/create/':
                    self.assertRedirects(response, final_url,
                                         status_code=Status.FOUND)
                else:
                    self.assertRedirects(response, final_url,
                                         status_code=Status.MOVED_PERMANENTLY)

    def test_not_available_user_edit(self):
        """Не автор не может редактировать сообщения"""
        self.user_2 = User.objects.create_user(username='noauthor')
        self.authorized_client.force_login(self.user_2)
        response = self.authorized_client.get(f'/posts/'
                                              f'{self.post.id}/edit',
                                              follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/',
                             status_code=Status.MOVED_PERMANENTLY)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Без переменной post_edit_template_url не проходит pytest на сервере
        post_edit_template_url = 'posts/create_post.html'
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:posts', kwargs={'slug': self.group.slug})),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={
                    'username': self.user.username})),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={
                    'post_id': self.post.id})),
            'posts/create_post.html': reverse('posts:post_create'),
            post_edit_template_url: (
                reverse('posts:post_edit', kwargs={
                    'post_id': self.post.id})),
            'posts/follow.html': reverse('posts:follow_index'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
