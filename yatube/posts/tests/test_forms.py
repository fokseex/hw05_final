import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

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
class FormTests(TestCase):
    """Класс тестирования Формы"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_change = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-slug-change',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """Проверка создания поста через форму"""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Запись создана',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        new_post = Post.objects.latest('pub_date')
        self.assertEqual(form_data['text'], new_post.text)
        self.assertEqual(form_data['group'], new_post.group.id)
        self.assertEqual(new_post.image, 'posts/small.gif')
        self.assertRedirects(response, f'/profile/{self.user.username}/')

    def tests_edit_post(self):
        """Проверка редактирования поста через форму"""
        uploaded = SimpleUploadedFile(
            name='other_small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактировано',
            'group': self.group_change.id,
            'image': uploaded,

        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        edit_post = Post.objects.get(id=self.post.id)
        self.assertEqual(form_data['text'], edit_post.text)
        self.assertEqual(form_data['group'], edit_post.group.id)
        self.assertEqual(edit_post.image, 'posts/other_small.gif')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_add_comments(self):
        """Проверка комментарий делает только авторизованный пользователь"""
        form_data = {
            'text': 'Комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.id}), data=form_data, follow=True)
        comment = Comment.objects.get(id=self.post.id)
        self.assertEqual(form_data['text'], comment.text)
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_only_authorized_add_comments(self):
        """Неавторизованный user перенаправляется на страницу логина"""
        form_data = {
            'text': 'Комментарий',
        }
        response = self.client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.id}), data=form_data, follow=True)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/'
                             f'{self.post.id}/comment/')
        self.assertEqual(Comment.objects.count(), 0)
