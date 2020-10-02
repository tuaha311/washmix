import dramatiq
from periodiq import cron

from pickups.models import Delivery, Schedule


# every day at 06:00
@dramatiq.actor(periodic=cron("00 06 * * *"))
def create_recurring_delivery_every_day():
    schedule_list = Schedule.objects.exclude(days=[])

    for schedule in schedule_list:
        delivery = Delivery()
        delivery = Delivery.objects.fill_delivery(schedule, delivery)
        delivery.save()
