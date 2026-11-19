from datetime import timedelta

from django.utils import timezone

MIN_DAYS = 5
MAX_DAYS = 7


def delivery_window(moment=None):
    moment = moment or timezone.localtime()
    if timezone.is_naive(moment):
        day = moment.date()
    else:
        day = timezone.localtime(moment).date()
    return day + timedelta(days=MIN_DAYS), day + timedelta(days=MAX_DAYS)


def window_for_order(order):
    start = order.expected_delivery_start
    end = order.expected_delivery_end
    if start and end:
        return start, end
    return delivery_window(order.createAT)
