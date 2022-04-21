from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from yatube.settings import TITLE_SYMBOL_VIEW


User = get_user_model()


class PostModelTest(TestCase):
    """Класс тестирования модели Post"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='g' * 30,
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='t' * 30,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        group_object_name = group.title
        post_object_name = post.text
        self.assertEqual(group_object_name, str(group))
        self.assertEqual(post_object_name[:TITLE_SYMBOL_VIEW], str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',

        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)
