from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from .tasks import process_tracker_data  # Import the Celery task
from django.http import HttpResponseBadRequest
from .forms import FleetOwnerForm, CarForm, TrackerForm, DriverForm, RFIDForm
from .models import FleetOwner, Tracker_data, Car, GPSTracker, Driver, RFID
from django.utils import timezone

# Create your views here.
# from login_required import login_not_required


# - Login
# @login_not_required
def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('')  # Update with your dashboard URL name
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {})


# - Sign Up
# @login_not_required
def signup(request):
    return render(request, 'sign_up.html')


# - Add Fleet Owner
def add_fleet_owner(request):
    if request.method == 'POST':
        form = FleetOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('fleet_owner_list')  # Redirect to a view that displays the list of fleet owners
    else:
        form = FleetOwnerForm()

    return render(request, 'add_fleet_owner.html', {'form': form})


# - Fleet Owner List
def fleet_owner_list(request):
    fleetowners = FleetOwner.objects.all()
    return render(request, 'fleet_owner_list.html', context={'fleetowners': fleetowners})

# - Update FleetOwner
def update_fleetowner(request, id):
    fleetowner = get_object_or_404(FleetOwner, pk=id)
    if request.method == 'POST':
        form = FleetOwnerForm(request.POST, instance=fleetowner)
        if form.is_valid():
            form.save()
            return redirect('fleet_owner_list')  # Adjust the URL name based on your setup
    else:
        form = FleetOwnerForm(instance=fleetowner)
    return render(request, 'update_fleetowner.html', {'form': form, 'fleetowner': fleetowner})
# - Tracker Data

def add_tracker_data(request):
    if request.method == 'GET':
        # Process incoming GPS tracker data
        data = parse_gps_tracker_data(request)
        print("Parsed Data:  ", data)
        # Enqueue Celery task to process data
        process_tracker_data.delay(data)

        # Return a response to the tracker acknowledging receipt
        return HttpResponse("Data received and queued for processing.")
    else:
        return HttpResponse("Please check data which is passed")


def parse_gps_tracker_data(request):
    try:
        registration_number = request.GET.get('car')
        zone = request.GET.get('zone')
        vendor = request.GET.get('vendor')
        auth_key = request.GET.get('auth_key')
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        speed = request.GET.get('speed')
        accuracy = request.GET.get('accuracy')
        panic = request.GET.get('panic')
        ignition = request.GET.get('ignition')
        air_condition = request.GET.get('air_condition')

        # Check if required fields are present
        if (registration_number is None or zone is None or vendor is None or auth_key is None or
                latitude is None or longitude is None or speed is None or accuracy is None or panic is None or
                ignition is None or air_condition is None):
            raise ValueError("Missing required fields in GPS tracker data")

        # Convert necessary fields to appropriate data types if needed
        car_registration_number = str(registration_number)

        try:
            # Check if the car registration number exists in the Car table
            car = Car.objects.get(registration_number=car_registration_number)
        except Car.DoesNotExist:
            return JsonResponse({'error': 'Car not found'}, status=400)

        # Use filter() instead of get() to handle multiple instances
        tracker_data_instances = Tracker_data.objects.filter(car=car)

        if tracker_data_instances.exists():
            # If there are multiple instances, update the first one
            tracker_data = tracker_data_instances.first()
        else:
            # If no instance exists, create a new one
            tracker_data = Tracker_data(car=car)

        # Update or set the tracker data fields
        tracker_data.zone = str(zone)
        tracker_data.vendor = str(vendor)
        tracker_data.auth_key = str(auth_key)
        tracker_data.latitude = float(latitude)
        tracker_data.longitude = float(longitude)
        tracker_data.speed = float(speed)
        tracker_data.accuracy = float(accuracy)
        tracker_data.panic = bool(panic)
        tracker_data.ignition = bool(ignition)
        tracker_data.air_condition = float(air_condition)

        # Save the tracker data instance
        tracker_data.save()

        # Return a dictionary with the extracted data
        return {
            'car': car_registration_number,
            'zone': zone,
            'vendor': vendor,
            'auth_key': auth_key,
            'latitude': float(latitude),
            'longitude': float(longitude),
            'speed': float(speed),
            'accuracy': float(accuracy),
            'panic': bool(panic),
            'ignition': bool(ignition),
            'air_condition': float(air_condition)
        }
    except (ValueError, TypeError) as e:
        # Log or handle the error as needed
        return JsonResponse({'error': "Invalid GPS tracker data: {}".format(str(e))}, status=400)
    except Exception as e:
        # Log or handle other unexpected errors
        return JsonResponse({'error': "Error processing GPS tracker data: {}".format(str(e))}, status=500)

# def parse_gps_tracker_data(request):
#     try:
#         registration_number = request.GET.get('car')
#         zone = request.GET.get('zone')
#         vendor = request.GET.get('vendor')
#         auth_key = request.GET.get('auth_key')
#         latitude = request.GET.get('latitude')
#         longitude = request.GET.get('longitude')
#         speed = request.GET.get('speed')
#         accuracy = request.GET.get('accuracy')
#         panic = request.GET.get('panic')
#         ignition = request.GET.get('ignition')
#         air_condition = request.GET.get('air_condition')
#
#
#         # Check if required fields are present
#         if (registration_number is None or zone is None or vendor is None or auth_key is None or
#                 latitude is None or longitude is None or speed is None or accuracy is None or panic is None or
#                 ignition is None or air_condition is None):
#             raise ValueError("Missing required fields in GPS tracker data")
#
#
#
#         # Convert necessary fields to appropriate data types if needed
#         car = str(registration_number)
#         zone = str(zone)
#         vendor = str(vendor)
#         auth_key = str(auth_key)
#         latitude = float(latitude)
#         longitude = float(longitude)
#         speed = float(speed)
#         accuracy = float(accuracy)
#         panic = bool(panic)
#         ignition = bool(ignition)
#         air_condition = float(air_condition)
#
#         # Return a dictionary with the extracted data
#         return {
#             'car': car,
#             'zone': zone,
#             'vendor': vendor,
#             'auth_key': auth_key,
#             'latitude': latitude,
#             'longitude': longitude,
#             'speed': speed,
#             'accuracy': accuracy,
#             'panic': panic,
#             'ignition': ignition,
#             'air_condition': air_condition
#             # 'timestamp': timestamp,
#             # Add other relevant fields if needed
#         }
#     except (ValueError, TypeError) as e:
#         # Log or handle the error as needed
#         return HttpResponseBadRequest("Invalid GPS tracker data: {}".format(str(e)))
#     except Exception as e:
#         # Log or handle other unexpected errors
#         return HttpResponseBadRequest("Error processing GPS tracker data: {}".format(str(e)))



# def add_tracker_data(request):
#     if request.method == 'GET':
#         registration_number = request.GET.get('car')
#         zone = request.GET.get('zone')
#         vendor = request.GET.get('vendor')
#         auth_key = request.GET.get('auth_key')
#         latitude = request.GET.get('latitude')
#         longitude = request.GET.get('longitude')
#         speed = request.GET.get('speed')
#         accuracy = request.GET.get('accuracy')
#         panic = request.GET.get('panic')
#         ignition = request.GET.get('ignition')
#         air_condition = request.GET.get('air_condition')
#
#         try:
#             car = Car.objects.get(registration_number=registration_number)
#         except Car.DoesNotExist:
#             return JsonResponse({'error': 'Car not found'}, status=400)
#
#         # tracker_data, created = Tracker_data.objects.get_or_create(car=car)
#
#         # Use filter() instead of get() to handle multiple instances
#         tracker_data_instances = Tracker_data.objects.filter(car=car)
#         print(tracker_data_instances)
#         if tracker_data_instances.exists():
#             # If there are multiple instances, update the first one
#             tracker_data = tracker_data_instances.first()
#             print(tracker_data)
#         else:
#             # If no instance exists, create a new one
#             tracker_data = Tracker_data(car=car)
#
#         tracker_data.zone = zone
#         tracker_data.vendor = vendor
#         tracker_data.auth_key = auth_key
#         tracker_data.latitude = latitude
#         tracker_data.longitude = longitude
#         tracker_data.speed = speed
#         tracker_data.accuracy = accuracy
#         tracker_data.timestamp = timezone.now()
#         tracker_data.panic = panic
#         tracker_data.ignition = ignition
#         tracker_data.air_condition = air_condition
#         # print(tracker_data.zone)
#         # tracker_data.save()
#         # print(tracker_data)
#         # Dispatch the Celery task asynchronously
#         process_tracker_data.delay(tracker_data)
#         # process_tracker_data_async.delay(tracker_data.id)
#         # process_tracker_data_async.delay(registration_number, zone, vendor, auth_key, latitude, longitude, speed, accuracy, panic, ignition, air_condition)
#         return JsonResponse({'success': 'Data received and queued for processing.'})
#         # return JsonResponse({'success': 'Data updated successfully'})
#         # return render(request, 'dashboard.html', {'tracker_data': tracker_data})
#         # return redirect('/')
#     else:
#         # return JsonResponse({'error': 'Invalid request method'}, status=405)
#         return render(request, 'error.html')


# @login_required
def tracker_data(request):
    tracker_data_list = Tracker_data.objects.all()
    # tracker_data_list = Tracker_data.objects.filter(user=request.user)
    total_count = Tracker_data.objects.count()  # Get the total count of rows
    # Get count of active cars
    # active_count = Tracker_data.objects.filter(status='active').count()

    # Get count of inactive cars
    # inactive_count = Tracker_data.objects.filter(status='inactive').count()

    return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list, 'total_count': total_count})


def tracker_data1(request):
    tracker_data_list = Tracker_data.objects.all()
    return render(request, 'dashboard1.html', context={'tracker_data_list': tracker_data_list})

# - Add Car
# def add_car(request):
#     if request.method == 'POST':
#         form = CarForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('car_list')  # Redirect to a view that displays the list of cars
#     else:
#         form = CarForm()
#
#     return render(request, 'add_car.html', {'form': form})

def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)

            # Check if a tracker with the provided serial number exists
            tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
            if tracker_serial_number:
                tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
                car.tracker = tracker

            car.save()
            return redirect('car_list')  # Adjust the URL name based on your setup
    else:
        form = CarForm()

    return render(request, 'add_car.html', {'form': form})


# - Car List
def car_list(request):
    car_list = Car.objects.all()
    # car_list = Car.objects.filter(user=request.user)
    return render(request, 'car_list.html', context={'car_list': car_list})

# Update Car
def update_car(request, id):
    car = get_object_or_404(Car, pk=id)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car_list')  # Adjust the URL name based on your setup
    else:
        form = CarForm(instance=car)
    return render(request, 'update_car.html', {'form': form, 'car': car})
# - Add Driver
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('driver_list')
    else:
        form = DriverForm()
    return render(request, 'add_driver.html', {'form': form})

def driver_list(request):
    drivers_list = Driver.objects.all()
    # drivers_list = Driver.objects.filter(user=request.user)
    return render(request, 'driver_list.html', context={'drivers_list': drivers_list})

def update_driver(request, id):
    driver = get_object_or_404(Driver, pk=id)
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('driver_list')  # Adjust the URL name based on your setup
    else:
        form = DriverForm(instance=driver)
    return render(request, 'update_driver.html', {'form': form, 'driver': driver})


def delete_driver(request, id):
    driver = get_object_or_404(Driver, id=id)
    if request.method == 'POST':
        driver.delete()
        return redirect('driver_list')  # Replace with your actual driver list URL name

    return render(request, 'delete_driver.html', {'driver': driver})



# - Add Tracker
def add_tracker(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tracker_list')
    else:
        form = TrackerForm()
    return render(request, 'add_tracker.html', {'form': form})



# - Tracker List
def tracker_list(request):
    tracker_list = GPSTracker.objects.all()
    return render(request, 'tracker_list.html', {'tracker_list': tracker_list})


# - Add RFID
def add_rfid(request):
    if request.method == 'POST':
        form = RFIDForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rfid_list')  # Redirect to a view that displays the list of RFIDs
    else:
        form = RFIDForm()

    return render(request, 'add_rfid.html', {'form': form})

# - RFID List
def rfid_list(request):
    rfid_list = RFID.objects.all()
    return render(request, 'rfid_list.html', {'rfid_list': rfid_list})


def update_rfid(request, id):
    rfid = get_object_or_404(RFID, pk=id)
    if request.method == 'POST':
        form = RFIDForm(request.POST, instance=rfid)
        if form.is_valid():
            form.save()
            return redirect('rfid_list')  # Adjust the URL name based on your setup
    else:
        form = RFIDForm(instance=rfid)
    return render(request, 'update_rfid.html', {'form': form, 'rfid': rfid})


def delete_rfid(request, id):
    rfid = get_object_or_404(RFID, id=id)
    if request.method == 'POST':
        rfid.delete()
        return redirect('rfid_list')  # Replace with your actual driver list URL name

    return render(request, 'delete_rfid.html', {'rfid': rfid})



@login_required
def profile(request):
    return render(request, 'registration/profile.html')