import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import COUNT_POST_VIEWS

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.no_correct_group = Group.objects.create(
            title='Группа без сообщений',
            slug='no-correct-group',
            description='Тестовое описание',
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group,
                image=uploaded,
            )
        cls.post_cash = Post.objects.create(
            author=cls.user,
            text='Тестируем caсhe',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def tests_first_page_contains_ten_records(self):
        # На 1 странице должно быть 10 постов
        diff_posts = Post.objects.all().count() - COUNT_POST_VIEWS
        page_list = {
            'Главная страница 1': reverse('posts:index'),
            'Страница групп 1': reverse('posts:posts', kwargs={
                'slug': self.group.slug}),
            'Страница профиля 1': reverse('posts:profile', kwargs={
                'username': self.user.username}),
            'Главная страница 2': reverse('posts:index') + '?page=2',
            'Страница групп 2': (reverse('posts:posts', kwargs={
                'slug': self.group.slug}) + '?page=2'),
            'Страница профиля 2': (reverse('posts:profile', kwargs={
                'username': self.user.username}) + '?page=2'),

        }
        for template, reverse_name in page_list.items():
            with self.subTest():
                response = self.client.get(reverse_name)
                if '1' in template:
                    self.assertEqual(len(response.context['page_obj']),
                                     COUNT_POST_VIEWS)
                else:
                    self.assertEqual(len(response.context['page_obj']),
                                     diff_posts)

    def test_group_wo_posts(self):
        # Группа без сообщений не содержит сообщений
        response = self.client.get(reverse('posts:posts', kwargs={
            'slug': self.no_correct_group.slug}))
        self.assertEqual(len(response.context['page_obj']), 0)

    def tests_page_index_group_profile_show_correct_context(self):
        """Шаблон сформированы с правильным контекстом"""
        page_list = {
            'Главная страница': reverse('posts:index'),
            'Страница групп': reverse('posts:posts', kwargs={
                'slug': self.group.slug}),
            'Страница профиля': reverse('posts:profile', kwargs={
                'username': self.user.username}),
            'Страница поста': reverse('posts:post_detail', kwargs={
                'post_id': self.post.id})
        }
        for template, reverse_name in page_list.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                if template == 'Страница поста':
                    post_count_variable = response.context['author_posts']
                    posts_count = (Post.objects.filter(
                        author=self.post.author).count())
                    self.assertEqual(post_count_variable, posts_count,
                                     msg='тест пройдет')
                    post = response.context['post']
                else:
                    post = response.context['page_obj'][0]
                post_id = post.id
                post_image = post.image
                post_author = post.author
                post_text = post.text
                post_group = post.group
                self.assertEqual(post_image, self.post.image)
                self.assertEqual(post_id, self.post.id)
                self.assertEqual(post_author, self.post.author)
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group, self.post.group)

    def test_correct_form_post_create(self):
        """Шаблон post create сформирован правильно"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_form_post_edit(self):
        """Шаблон post edit сформирован правильно"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
