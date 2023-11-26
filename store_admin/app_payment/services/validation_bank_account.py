from typing import Tuple, Optional, List

from django.utils.translation import gettext as _

from random import choice

ERRORS_LIST = [
    _('Error 1. Number of account is odd or ends with zero.'),
    _('Error 2. We could not handle payment'),
    _('Error 3. You have account another bank'),
]

TRUE_LIST_DIGIT = [2, 4, 6, 8]


def validation_number_account(number: str) -> Tuple[bool, Optional[List[str]]]:
    """
    Проверка номера счета или карты.
    :param number: номер счета из формы,
    :return: кортеж, где первое значение верное/неверное,
            второе - текст ошибки, при не подходящем номере.
    """
    number = number.replace(' ', '')
    last_digit = int(number[-1])
    if last_digit in TRUE_LIST_DIGIT:
        return True, None
    return False, choice(ERRORS_LIST)
