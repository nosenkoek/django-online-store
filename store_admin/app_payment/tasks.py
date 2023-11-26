from datetime import datetime
from time import sleep

from celery import shared_task

from app_order.models import Order
from app_payment.services.validation_bank_account import \
    validation_number_account


@shared_task
def payment_task(order_id: str, number: str) -> None:
    """
    Задача для оплаты заказа
    :param order_id: id заказа
    :param number: номер карты или счета
    """
    sleep(7)
    order = Order.objects.select_related('payment_fk').get(order_id=order_id)
    payment = order.payment_fk
    result, error = validation_number_account(number)

    if result:
        order.status = 'paid'
        payment.paid = datetime.now()
        payment.error = None
    else:
        payment.error = error

    payment.save()
    order.save()
