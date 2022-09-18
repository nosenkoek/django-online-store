from django.test import TestCase


class SearchResultProductListTest(TestCase):
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
