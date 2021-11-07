from django.test import Client, TestCase
from django.urls import reverse

ABOUT_AUTHOR = reverse('about:author')
ABOUT_TECH = reverse('about:tech')


class PostPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_uses_correct_template(self):
        """ Urls about are using correct template. """
        templates_pages_names = {
            ABOUT_AUTHOR: 'about/author.html',
            ABOUT_TECH: 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(
                    reverse_name, follow=True
                )
                self.assertTemplateUsed(response, template)
