from django.test import TestCase

from ..models import Group, Post, User

USERNAME = 'auth'
TITLE = 'test-title'
SLUG = 'test-slug'
DESCRP = 'test-descrp'
PUB_DATE = 'test-pub_date'
TEXT = 'test-text'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRP,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_have_correct_object_text(self):
        post = PostModelTest.post
        expected_object_text = post.text
        self.assertEqual(expected_object_text, str(post))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.author = User.objects.create_user(username='TestName2')
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRP,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT,
        )

    def test_models_have_correct_object_names(self):
        group = FollowModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_have_correct_object_text(self):
        post = FollowModelTest.post
        expected_object_text = post.text
        self.assertEqual(expected_object_text, str(post))
