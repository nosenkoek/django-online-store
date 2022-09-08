import re
from typing import Optional

from django import template

from app_products.services.settings import PATTERN_URL

register = template.Library()


@register.simple_tag
def solve_url(value: str, field_name: str,
              urlencode: Optional[str] = None) -> str:
    """
    Шаблонный тэг для расчета "сборного" URL сортировка-фильтр-пагинация
    :param value: значение фильтра/страницы/поля сортировки
    :param field_name: поле фильтра/sort/page
    :param urlencode: параметры запроса
    :return: собранный url-адрес
    """
    url = f'?{field_name}={value}'

    if urlencode:
        querystring = re.findall(PATTERN_URL, urlencode)

        filtered_querystring = filter(
            lambda param: param.split('=')[0] != field_name,
            querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = f'{url}&{encoded_querystring}'

    return url


@register.simple_tag
def url_clear_filter(value: str) -> str:
    """
    Шаблонный тег для расчета URL при очистке фильтра
    :param value: значение query в запросе поиска
    :return: url-адрусс
    """
    url = f'?query={value}'
    return url
