from django import template

from app_products.templatetags.tags import solve_url

register = template.Library()
register.simple_tag(solve_url)


@register.simple_tag
def url_clear_filter(value: str) -> str:
    """
    Шаблонный тег для расчета URL при очистке фильтра
    :param value: значение query в запросе поиска
    :return: url-адрусс
    """
    url = f'?query={value}'
    return url
