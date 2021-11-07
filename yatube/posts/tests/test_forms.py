import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

POST_CREATE_URL = reverse("posts:post_create")
USERNAME = 'TestName1'
TITLE = 'test-title'
SLUG = 'test-slug'
DESCRP = 'test-descrp'
PUB_DATE = 'test-pub_date'
TEXT = 'test-text'
TEXT_COM = 'test-com-text'
IMAGE = 'posts/small.gif'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post_profile_url = reverse(
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
        cls.post = Post.objects.create(
            author=cls.user,
            pub_date=PUB_DATE,
            text=TEXT,
            group=cls.group,
        )
        cls.post_edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.pk}
        )
        cls.post_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.pk}
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """ Valid form create post in Post. """
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'author': self.user,
            'group': self.group.pk,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.post_profile_url)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=TEXT,
                author=self.user,
                group=self.group,
                image=IMAGE,
            ).exists()
        )

    def test_edit_post(self):
        """ Valid form edit post in Post. """
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'author': self.user,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            self.post_edit_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.post_detail_url)
        self.assertEqual(Post.objects.count(), post_count)
        last_post = Post.objects.order_by('id').last()
        self.assertEqual(last_post.text, TEXT)
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, self.group)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CommentCreateFormTests(TestCase):
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
            pub_date=PUB_DATE,
            text=TEXT,
            group=cls.group,
        )
        cls.comment_create_url = reverse(
            "posts:add_comment", kwargs={'post_id': cls.post.pk}
        )
        cls.post_detail_url = reverse(
            "posts:post_detail", kwargs={'post_id': cls.post.pk}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_comment(self):
        """ Create comment. """
        comment_count = Comment.objects.count()
        form_data = {
            'text': TEXT_COM,
        }
        response = self.authorized_client.post(
            self.comment_create_url,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.post_detail_url)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text=TEXT_COM,
                post=self.post,
            ).exists()
        )
