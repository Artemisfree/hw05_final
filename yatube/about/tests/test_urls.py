from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_urls(self):
        static_urls_names = {
            '/about/author/',
            '/about/tech/',
        }
        for url_name in static_urls_names:
            with self.subTest(url_name=url_name):
                response = self.guest_client.get(url_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
