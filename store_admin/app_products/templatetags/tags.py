import re
from typing import Optional

from django import template

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
        querystring = re.findall(r"([^&]*=[^&]{1,})", urlencode)

        filtered_querystring = filter(
            lambda param: param.split('=')[0] != field_name,
            querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = f'{url}&{encoded_querystring}'

    return url
