import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POSTS_INDEX_URL = reverse('posts:index')
POSTS_CREATE_URL = reverse('posts:post_create')
USERNAME = 'TestName1'
TITLE = 'test-title'
TITLE_TWO = 'test-title_two'
SLUG = 'test-slug'
SLUG_TWO = 'test-slug_two'
DESCRP = 'test-descrp'
DESCRP_TWO = 'test-descrp_two'
PUB_DATE = 'test-pub_date'
TEXT = 'test-text'
TEXT_TWO = 'test-text_two'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.posts_profile_url = reverse(
            'posts:profile', kwargs={'username': cls.user}
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRP,
        )
        cls.posts_group_list_url = reverse(
            'posts:group_list', kwargs={'slug': SLUG}
        )
        cls.group_two = Group.objects.create(
            title=TITLE_TWO,
            slug=SLUG_TWO,
            description=DESCRP_TWO
        )
        cls.posts_group_list_two_url = reverse(
            'posts:group_list', kwargs={'slug': cls.group_two.slug}
        )
        cls.post = Post.objects.create(
            author=cls.user,
            pub_date=PUB_DATE,
            text=TEXT,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.posts_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk}
        )
        cls.posts_edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.pk}
        )
        cls.post_two = Post.objects.create(
            author=cls.post.author,
            text=TEXT_TWO,
            group=cls.group_two,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """ Urls are using correct template. """
        templates_pages_names = {
            POSTS_INDEX_URL: 'posts/index.html',
            self.posts_group_list_url: 'posts/group_list.html',
            self.posts_profile_url: 'posts/profile.html',
            self.posts_detail_url: 'posts/post_detail.html',
            POSTS_CREATE_URL: 'posts/create_post.html',
            self.posts_edit_url: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """ Template index has correct context. """
        cache.clear()
        response = self.authorized_client.get(POSTS_INDEX_URL)
        first_object = response.context['page_obj'][1]
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_text_0 = first_object.text
        posts_group_0 = first_object.group
        posts_image_0 = first_object.image

        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_group_0, self.post.group)
        self.assertEqual(posts_image_0, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """ Template group_list has correct template. """
        response = self.authorized_client.get(self.posts_group_list_url)
        first_object = response.context['page_obj'][0]
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_text_0 = first_object.text
        posts_group_0 = first_object.group
        posts_image_0 = first_object.image

        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_group_0, self.post.group)
        self.assertEqual(posts_image_0, self.post.image)

    def test_profile_page_show_correct_context(self):
        """ Template profile has correct context. """
        response = self.authorized_client.get(self.posts_profile_url)
        first_object = response.context['page_obj'][1]
        posts_pub_date_0 = first_object.pub_date
        posts_author_0 = first_object.author
        posts_text_0 = first_object.text
        posts_group_0 = first_object.group
        posts_image_0 = first_object.image

        self.assertEqual(posts_pub_date_0, self.post.pub_date)
        self.assertEqual(posts_author_0, self.post.author)
        self.assertEqual(posts_text_0, self.post.text)
        self.assertEqual(posts_group_0, self.post.group)
        self.assertEqual(posts_image_0, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """ Template post_detail has correct context. """
        response = self.authorized_client.get(self.posts_detail_url)
        self.assertEqual(
            response.context.get('post').pub_date, self.post.pub_date
        )
        self.assertEqual(
            response.context.get('post').author, self.post.author
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(
            response.context.get('post').group, self.post.group
        )
        self.assertEqual(
            response.context.get('post').image, self.post.image
        )

    def test_create_edit_page_show_correct_context(self):
        """ Templates create and edit has correct context. """
        create_urls = [
            POSTS_CREATE_URL,
            self.posts_edit_url,
        ]
        for url in create_urls:
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_in_uncorrect_group(self):
        """ Post in uncorrect group. """
        response = self.authorized_client.get(self.posts_group_list_two_url)
        argument = response.context['posts']
        self.assertNotIn(self.post, argument)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.posts_profile_url = reverse(
            'posts:profile', kwargs={'username': cls.user}
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRP,
        )
        cls.posts_group_url = reverse(
            'posts:group_list', kwargs={'slug': SLUG}
        )
        cls.posts_list = []
        for i in range(13):
            cls.posts_list.append(Post(
                author=cls.user,
                text=f'test-text {i}',
                group=cls.group,
            ))
        Post.objects.bulk_create(cls.posts_list)
        cls.paginator_pages = [
            POSTS_INDEX_URL,
            cls.posts_profile_url,
            cls.posts_group_url,
        ]

    def test_pages_contains_ten_records(self):
        """ Test for first and second page with records. """
        for reverse_page in self.paginator_pages:
            cache.clear()
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertEqual(len(response.context['page_obj']), 10)
            cache.clear()
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class FollowingTestViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author = User.objects.create_user(username='TestName2')
        cls.url_follow = reverse(
            'posts:profile_follow', kwargs={"username": cls.author.username}
        )
        cls.url_unfollow = reverse(
            'posts:profile_unfollow', kwargs={"username": cls.author.username}
        )

    def test_following_author(self):
        response = self.authorized_client.get(self.url_follow, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertTrue(
            Follow.objects.filter(
                author=self.author,
                user=self.user,
            ).exists()
        )

    def test_unfollowing_author(self):
        response = self.authorized_client.get(self.url_unfollow, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
