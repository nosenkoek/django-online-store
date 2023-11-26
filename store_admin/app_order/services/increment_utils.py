from django.db import connection


def get_next_increment() -> int:
    """
    Возвращает следующее значение инкремента из БД для номера заказа
    :return: следующее значение номера заказа
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT nextval('order_number_seq')")
        result = cursor.fetchone()
        return result[0]
