from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):

    # def setUp(self):
    #     self.guest_client = Client()

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        # Проверьте, что статус ответа сервера - 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверьте, что используется шаблон core/404.html
        self.assertTemplateUsed(response, 'core/404.html')
