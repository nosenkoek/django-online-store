from django.test import TestCase
from django.db import connection


class SearchResultProductListTest(TestCase):
    fixtures = ['app_search/tests/fixtures/fixtures_test_search_model.json']

    @classmethod
    def setUpClass(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute(open('..\\schema_design\\init.sql', 'r').read())

        super(SearchResultProductListTest, cls).setUpClass()

    def setUp(self) -> None:
        self.main_url = '/search/?query=text'

    def test_search_result_products_list_url(self):
        """Проверка открытия с результатом списка товаров"""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_products_list_template(self):
        """Проверка используемого шаблона"""
        response = self.client.get(self.main_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'app_search/search_list.html')
