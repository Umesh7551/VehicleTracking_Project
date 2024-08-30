# tasks.py
from celery import shared_task, current_task
from django.db import DatabaseError
from .models import Tracker_data
from .utils import send_tracker_data_to_api
import time
@shared_task
def process_tracker_data(data):
    # print(data)
    try:
        # Process and save data to the tracker_data table

        Tracker_data.objects.create(**data)

        # print(Tracker_data)
    except DatabaseError as exc:
        # Retry the task if there's a database error
        current_task.retry(exc=exc, countdown=60)  # Retry after 60 seconds
# @shared_task
# def process_tracker_data_async(tracker_data_id):
#     # Retrieve Tracker_data instance by ID
#     tracker_data = Tracker_data.objects.get(id=tracker_data_id)
#     print(tracker_data)
#
#     # Perform any additional processing if needed
#     # ...
#
#     # Save the changes
#     tracker_data.save()


# tasks.py
# from celery import shared_task
# from .models import Tracker_data, Car
#
# @shared_task
# def process_tracker_data_async(car_registration_number, tracker_data_id):
#     # Retrieve Car instance by registration number
#     car = Car.objects.get(registration_number=car_registration_number)
#     print(car)
#     # Retrieve Tracker_data instance by ID
#     tracker_data = Tracker_data.objects.get(id=tracker_data_id, car=car)
#     print(tracker_data)
#     # Perform any additional processing if needed
#     # ...
#
#     # Save the changes
#     tracker_data.save()



# your_app/tasks.py
# from celery import shared_task
# from django.utils import timezone
# from .models import Tracker_data, Car
#
# @shared_task
# def process_tracker_data_async(registration_number, zone, vendor, auth_key, latitude, longitude, speed, accuracy, panic, ignition, air_condition):
#     try:
#         car = Car.objects.get(registration_number=registration_number)
#     except Car.DoesNotExist:
#         print(f'Car with registration number {registration_number} not found.')
#         return
#
#     tracker_data_instances = Tracker_data.objects.filter(car=car)
#
#     if tracker_data_instances.exists():
#         tracker_data = tracker_data_instances.first()
#     else:
#         tracker_data = Tracker_data(car=car)
#
#     tracker_data.zone = zone
#     tracker_data.vendor = vendor
#     tracker_data.auth_key = auth_key
#     tracker_data.latitude = latitude
#     tracker_data.longitude = longitude
#     tracker_data.speed = speed
#     tracker_data.accuracy = accuracy
#     tracker_data.timestamp = timezone.now()
#     tracker_data.panic = panic
#     tracker_data.ignition = ignition
#     tracker_data.air_condition = air_condition
#
#     tracker_data.save()
#
#     print(f'Tracker_data for car {registration_number} updated successfully.')



@shared_task
def send_tracker_data_periodically():
    while True:
        send_tracker_data_to_api(None)  # Sending tracker data
        time.sleep(10)  # Wait for 10 seconds before sending the next update