from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User

USERNAME = 'TestName1'
TITLE = 'test-title'
SLUG = 'test-slug'
DESCRP = 'test-descrp'
PUB_DATE = 'test-pub_date'
TEXT = 'test-text'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRP,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT,
            pub_date=PUB_DATE,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_static_urls_posts_guest_client(self):
        static_urls_names = {
            '/',
            '/group/test-slug/',
            f'/profile/{StaticURLTests.user.username}/',
            f'/posts/{StaticURLTests.post.pk}/',
        }
        for url_name in static_urls_names:
            cache.clear()
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_post(self):
        if self.user == StaticURLTests.post.author:
            response = self.authorized_client.get(
                f'/posts/{StaticURLTests.post.pk}/edit/'
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
