import time

from django.contrib.auth.decorators import login_required
# from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .tasks import process_tracker_data  # Import the Celery task
# from django.http import HttpResponseBadRequest
from .forms import FleetOwnerForm, CarForm, TrackerForm, DriverForm, RFIDForm, SignUpForm, LoginForm
from .models import FleetOwner, Tracker_data, Car, GPSTracker, Driver, RFID
# from django.utils import timezone

# Create your views here.
# from login_required import login_not_required

# - Index page This will be first page of application


# @login_not_required
def index(request):
    return render(request, 'index.html')


# - SignUp
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to database yet
            user.password = make_password(form.cleaned_data['password1'])  # Hash the password
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# - Login


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print(password)
        # Authenticate the user against FleetOwner model
        user = authenticate(request, username=username, password=password)
        # print(user)
        if user is not None:
            # User authentication successful
            django_login(request, user)  # Log the user in
            return redirect('profile')  # Redirect to profile page
        else:
            # Authentication failed
            return render(request, 'registration/login.html', {'error': 'Invalid email or password'})
    else:
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})



# - Add Fleet Owner
@login_required
def add_fleet_owner(request):
    if request.method == 'POST':
        form = FleetOwnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fleet owner added successfully.')  # Add success message
            return redirect('fleet_owner_list')  # Redirect to a view that displays the list of fleet owners
        else:
            messages.error(request, 'Failed to add fleet owner. Please check the form.')  # Add error message
    else:
        form = FleetOwnerForm()

    return render(request, 'add_fleet_owner.html', {'form': form})


# - Fleet Owner List
@login_required
def fleet_owner_list(request):
    fleetowners = FleetOwner.objects.all()
    return render(request, 'fleet_owner_list.html', context={'fleetowners': fleetowners})

# - Update FleetOwner
@login_required
def update_fleetowner(request, id):
    fleetowner = get_object_or_404(FleetOwner, pk=id)
    if request.method == 'POST':
        form = FleetOwnerForm(request.POST, instance=fleetowner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fleet owner Updated successfully.')  # Add success message
            return redirect('fleet_owner_list')  # Adjust the URL name based on your setup
        else:
            messages.error(request, 'Failed to Update fleet owner. Please check the form.')  # Add error message
    else:
        form = FleetOwnerForm(instance=fleetowner)
    return render(request, 'update_fleetowner.html', {'form': form, 'fleetowner': fleetowner})
# - Tracker Data
@login_required
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


# @login_required
# def tracker_data(request):
#     tracker_data_list = Tracker_data.objects.all()
#     # tracker_data_list = Tracker_data.objects.filter(car__id=request.user.car.owner)
#     total_count = Tracker_data.objects.count()  # Get the total count of rows
#     # Get count of active cars
#     # active_count = Tracker_data.objects.filter(status='active').count()
#
#     # Get count of inactive cars
#     # inactive_count = Tracker_data.objects.filter(status='inactive').count()
#
#     return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list, 'total_count': total_count})

# @login_required
# def tracker_data(request):
#     if hasattr(request.user, 'car'):  # Check if the user has associated car
#         tracker_data_list = Tracker_data.objects.filter(car=request.user.car)
#         total_count = tracker_data_list.count()  # Get the total count of rows
#     else:
#         tracker_data_list = []
#         total_count = 0
#
#     return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list, 'total_count': total_count})

# @login_required
# def tracker_data(request):
#     if hasattr(request.user, 'fleetowner'):  # Check if the user is a fleet owner
#         cars = request.user.fleetowner.car_set.all()  # Get all cars associated with the fleet owner
#         print(cars)
#         tracker_data_list = Tracker_data.objects.filter(car__in=cars)
#         total_count = tracker_data_list.count()  # Get the total count of rows
#     # else:
#     #     tracker_data_list = []
#     #     total_count = 0
#         return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list, 'total_count': total_count})
#     else:
#         return HttpResponse("No Tracker Data Available!")

# @login_required
# def tracker_data(request):
#     if hasattr(request.user, 'fleetowner'):  # Check if the user is a fleet owner
#         cars = request.user.fleetowner.cars.all()  # Get all cars associated with the fleet owner
#         print("Cars", cars)
#         tracker_data_list = Tracker_data.objects.filter(car__in=cars)
#         print("Tracker Data List", tracker_data_list)
#         total_count = tracker_data_list.count()  # Get the total count of rows
#     # else:
#     #     tracker_data_list = []
#     #     total_count = 0
#
#         return render(request, 'dashboard.html', context={'tracker_data_list': tracker_data_list, 'total_count': total_count})
#     else:
#         return HttpResponse("No Tracker Data Available!")

# @login_required
# def tracker_data(request, fleetowner_id):
#     """
#     Retrieves tracker data associated with a specific FleetOwner.
#
#     Args:
#         request (HttpRequest): The incoming HTTP request.
#         fleetowner_id (int): The ID of the FleetOwner.
#
#     Returns:
#         HttpResponse: A rendered template with the retrieved tracker data or an error message
#                       if the FleetOwner is not found.
#     """
#
#     try:
#         fleetowner = FleetOwner.objects.get(pk=fleetowner_id)
#     except FleetOwner.DoesNotExist:
#         return render(request, 'error.html', {'message': 'FleetOwner not found'})
#
#     # Optimized query using car_set (assuming a ForeignKey relationship)
#     tracker_data_list = Tracker_data.objects.filter(car__fleetowner=fleetowner)
#
#     context = {'tracker_data_list': tracker_data_list, 'fleetowner': fleetowner}
#     return render(request, 'dashboard.html', context)

# @login_required  # Ensures user is logged in
# def tracker_data(request, fleetowner_id):
#     """
#     Retrieves tracker data associated with a specific FleetOwner.
#
#     Args:
#         request (HttpRequest): The incoming HTTP request.
#         fleetowner_id (int): The ID of the FleetOwner.
#
#     Returns:
#         HttpResponse: A rendered template with the retrieved tracker data or an error message
#                       if the FleetOwner is not found.
#     """
#
#     try:
#         fleetowner = FleetOwner.objects.get(pk=fleetowner_id)
#     except FleetOwner.DoesNotExist:
#         return render(request, 'error.html', {'message': 'FleetOwner not found'})
#
#     # Assuming a ForeignKey relationship between TrackerData and Car:
#     try:
#         # Extract car ID from URL (assuming the URL pattern captures it)
#         car_id = int(request.path_info.split('/')[2])
#         car = Car.objects.get(pk=car_id)  # Get the Car object based on ID
#     except (Car.DoesNotExist, ValueError):
#         return render(request, 'error.html', {'message': 'Invalid car ID'})
#
#     # Optimized query using car relationship
#     tracker_data_list = Tracker_data.objects.filter(car=car)
#
#     context = {'tracker_data_list': tracker_data_list, 'fleetowner': fleetowner}
#     return render(request, 'dashboard.html', context)

  # Assuming models in the same app

# @login_required  # Ensures user is logged in
# def tracker_data(request, id):
#     """
#     Retrieves tracker data associated with a specific FleetOwner.
#
#     Args:
#         request (HttpRequest): The incoming HTTP request.
#         fleetowner_id (int): The ID of the FleetOwner.
#
#     Returns:
#         HttpResponse: A rendered template with the retrieved tracker data or an error message
#                       if the FleetOwner is not found.
#     """
#
#     try:
#         fleetowner = FleetOwner.objects.get(pk=id)
#         print(fleetowner)
#     except FleetOwner.DoesNotExist:
#         return render(request, 'error.html', {'message': 'FleetOwner not found'})
#
#     # Assuming URL pattern captures car ID:
#     try:
#         # car_id = int(request.path_info.split('/')[2])
#         # print("Car Id: ", car_id)
#         # car = Car.objects.get(pk=car_id)  # Get the Car object based on ID
#         # print("Car:", car)
#         # Get the Car object(s) associated with the logged-in user's FleetOwner
#         cars = Car.objects.get(owner=fleetowner)
#         print("car: ", cars)
#         # Handle cases with no cars or a single car
#         if not cars.exists():
#             return render(request, 'error.html', {'message': 'No cars found for this FleetOwner'})
#         elif cars.count() == 100:
#             car = cars.first()
#
#     except (Car.DoesNotExist, ValueError):
#         return render(request, 'error.html', {'message': 'Invalid car ID'})
#
#     # Optimized query using car relationship
#     tracker_data_list = Tracker_data.objects.filter(car=car)
#
#     context = {'tracker_data_list': tracker_data_list, 'fleetowner': fleetowner}
#     return render(request, 'dashboard.html', context)

@login_required
def tracker_data(request, id):
    """
    Retrieves tracker data associated with a specific FleetOwner.

    Args:
        request (HttpRequest): The incoming HTTP request.
        id (int): The ID of the FleetOwner.

    Returns:
        HttpResponse: A rendered template with the retrieved tracker data or an error message
                      if the FleetOwner is not found.
    """

    try:
        fleetowner = FleetOwner.objects.get(pk=id)
    except FleetOwner.DoesNotExist:
        return render(request, 'error.html', {'message': 'FleetOwner not found'})

    # Retrieve all cars associated with the FleetOwner
    cars = Car.objects.filter(owner=fleetowner)

    # Check if any cars are associated with the FleetOwner
    if not cars.exists():
        return render(request, 'error.html', {'message': 'No cars found for this FleetOwner'})

    # Create an empty list to store tracker data for all cars
    tracker_data_list = []

    # Loop through each car and retrieve its tracker data
    for car in cars:
        # Retrieve tracker data for the current car
        tracker_data_for_car = Tracker_data.objects.filter(car=car)

        # Extend the tracker_data_list with the tracker data for the current car
        tracker_data_list.extend(tracker_data_for_car)

    context = {'tracker_data_list': tracker_data_list, 'fleetowner': fleetowner}
    return render(request, 'dashboard.html', context)





@login_required
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

@login_required
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
            messages.success(request, 'Car added successfully.')  # Add success message
            return redirect('car_list')  # Adjust the URL name based on your setup
        else:
            messages.error(request, 'Failed to add car. Please check the form.')  # Add error message
    else:
        form = CarForm()

    return render(request, 'add_car.html', {'form': form})


# - Car List
@login_required
def car_list(request):
    car_list = Car.objects.all()
    # car_list = Car.objects.filter(user=request.user)
    return render(request, 'car_list.html', context={'car_list': car_list})

# Update Car
@login_required
def update_car(request, id):
    car = get_object_or_404(Car, pk=id)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car Updated successfully.')  # Add success message
            return redirect('car_list')  # Adjust the URL name based on your setup
        else:
            messages.error(request, 'Failed to Update Car. Please check the form.')  # Add error message
    else:
        form = CarForm(instance=car)
    return render(request, 'update_car.html', {'form': form, 'car': car})
# - Add Driver
@login_required
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver added successfully.')  # Add success message
            return redirect('driver_list')
        else:
            messages.error(request, 'Failed to add Driver. Please check the form.')  # Add error message
    else:
        form = DriverForm()
    return render(request, 'add_driver.html', {'form': form})

@login_required
def driver_list(request):
    drivers_list = Driver.objects.all()
    # drivers_list = Driver.objects.filter(user=request.user)
    return render(request, 'driver_list.html', context={'drivers_list': drivers_list})
@login_required
def update_driver(request, id):
    driver = get_object_or_404(Driver, pk=id)
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Driver Updated successfully.')  # Add success message
            return redirect('driver_list')  # Adjust the URL name based on your setup
        else:
            messages.error(request, 'Failed to Update Driver. Please check the form.')  # Add error message
    else:
        form = DriverForm(instance=driver)
    return render(request, 'update_driver.html', {'form': form, 'driver': driver})

@login_required
def delete_driver(request, id):
    driver = get_object_or_404(Driver, id=id)
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Driver Deleted successfully.')  # Add success message
        return redirect('driver_list')  # Replace with your actual driver list URL name
    else:
        messages.error(request, 'Failed to Delete Driver. Please check the form.')  # Add error message

    return render(request, 'delete_driver.html', {'driver': driver})



# - Add Tracker
# def add_tracker(request):
#     if request.method == 'POST':
#         form = TrackerForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # return JsonResponse({'success': True})
#             # messages.success(request, 'Tracker added successfully.')  # Add success message
#             return redirect('tracker_list')
#         else:
#             pass
#             # return JsonResponse({'success': False, 'errors': form.errors})
#             # messages.error(request, 'Failed to add Tracker. Please check the form.')  # Add error message
#     else:
#         form = TrackerForm()
#     return render(request, 'add_tracker.html', {'form': form})
@login_required
def add_tracker(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors})
    else:
        form = TrackerForm()
    return render(request, 'add_tracker.html', {'form': form})




# - Tracker List
@login_required
def tracker_list(request):
    tracker_list = GPSTracker.objects.all()
    return render(request, 'tracker_list.html', {'tracker_list': tracker_list})


# - Add RFID
@login_required
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
@login_required
def rfid_list(request):
    rfid_list = RFID.objects.all()
    return render(request, 'rfid_list.html', {'rfid_list': rfid_list})

@login_required
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

@login_required
def delete_rfid(request, id):
    rfid = get_object_or_404(RFID, id=id)
    if request.method == 'POST':
        rfid.delete()
        return redirect('rfid_list')  # Replace with your actual driver list URL name

    return render(request, 'delete_rfid.html', {'rfid': rfid})


@login_required
def profile(request):
    username = request.user
    # Fetch user profile data from FleetOwner table based on the logged-in user
    fleet_owner = FleetOwner.objects.get(username=username)
    return render(request, 'registration/profile.html', {'fleet_owner': fleet_owner})


def logout_user(request):
    logout(request)
    return redirect('login')