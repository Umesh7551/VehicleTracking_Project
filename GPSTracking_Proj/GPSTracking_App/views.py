import time
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .tasks import process_tracker_data  # Import the Celery task
from .forms import CarForm, TrackerForm, DriverForm, RFIDForm, UserRegisterForm, LoginForm, UserUpdateForm, \
    ProfileUpdateForm, FleetOwnerSupportUserForm
from .models import Tracker_data, Car, GPSTracker, Driver, RFID, FleetOwnerSupport, Profile
from .utils import send_tracker_data_to_api
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.urls import reverse
# Create your views here.
# from login_required import login_not_required
from django.db import IntegrityError
# - Index page This will be first page of application


# @login_not_required
def index(request):
    return render(request, 'index.html')


# - Register User

def register(request):
    # form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')  # Assuming the form has an email field
            try:
                existing_user = User.objects.get(email=email)
                messages.error(request, f'A user {existing_user} with this email already exists.')
                return redirect('signup')  # Redirect back to the registration form
            except ObjectDoesNotExist:
                # Proceed with creating the user if the email is not already registered
                user = form.save(commit=False)
                user.is_active = False  # Deactivate account until email confirmation
                user.save()
                # Generate token and send email
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = token_generator.make_token(user)
                activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
                activation_url = f"http://{current_site.domain}{activation_link}"

                message = render_to_string('accounts/activation_email.html', {
                    'user': user,
                    'activation_url': activation_url,
                })
                email = EmailMessage(mail_subject, message, from_email='hindole.umesh@gmail.com', to=[user.email])
                email.send()

                messages.success(request, 'Please confirm your email to complete registration.')
                return redirect('login')  # Redirect to a success page
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/signup.html', {'form': form})


User = get_user_model()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Your Activation link is invalid!')
        return redirect('login')


# - Login
def user_login(request):
    # Check if user is already authenticated
    if request.user.is_authenticated:
        # Redirect to the appropriate dashboard based on user group
        if request.user.groups.filter(name="ed_admin").exists():
            return redirect('ed_admin_dashboard')
        elif request.user.groups.filter(name="ed_admin_support_person").exists():
            return redirect('ed_admin_support_dashboard')
        elif request.user.groups.filter(name="fleetowner").exists():
            return redirect('fleetowner_dashboard')
        elif request.user.groups.filter(name="fleetowner_support_person").exists():
            return redirect('fleetowner_support_dashboard')
        else:
            messages.warning(request, 'You have not been granted access to any dashboard!')
            return redirect('login')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # username = request.POST['username']  # Raises KeyError if 'username' is not provided
        # password = request.POST['password']  # Raises KeyError if 'password' is not provided
        # username = request.POST.get('username')  # Returns None if 'username' is not provided
        # password = request.POST.get('password')  # Returns None if 'password' is not provided
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            # print(password)
            # Authenticate the user against User model
            user = authenticate(request, username=username, password=password)
            # print(user)
            if user is not None:
                # Check if user is active
                if not user.is_active:
                    messages.error(request, 'Please activate your account first.')
                    return redirect('login')
                # User is active and authentication is successful
                login(request, user)  # Log the user in
                # Set session expiry based on 'remember me'
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close
                # return redirect('profile')  # Redirect to profile page
                if user.groups.filter(name="ed_admin").exists():
                    messages.success(request, 'You have successfully logged in')
                    return redirect('ed_admin_dashboard')
                elif user.groups.filter(name="ed_admin_support_person").exists():
                    messages.success(request, 'You have successfully logged in')
                    return redirect('ed_admin_support_dashboard')
                elif user.groups.filter(name="fleetowner").exists():
                    messages.success(request, 'You have successfully logged in')
                    return redirect('fleetowner_dashboard')
                elif user.groups.filter(name="fleetowner_support_person").exists():
                    messages.success(request, 'You have successfully logged in')
                    return redirect('fleetowner_support_dashboard')
                else:
                    messages.warning(request, 'Please contact administrator. You have not given permission to access application!!!')
                    return redirect('login')
            else:
                messages.error(request, 'Username or Password is incorrect!!!')
                form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required(login_url='login')
def ed_admin_dashboard(request):
    if request.user.groups.filter(name='ed_admin').exists():
        # Fetching users from the specified groups
        fleetowner_group = Group.objects.get(name='fleetowner')

        fleetowner_support_group = Group.objects.get(name='fleetowner_support_person')
        ed_admin_support_group = Group.objects.get(name='ed_admin_support_person')

        # Querying users in these groups
        fleetowners = User.objects.filter(groups=fleetowner_group)
        print("Fleetowners==============>", fleetowners)
        fleetowner_supports = User.objects.filter(groups=fleetowner_support_group)
        ed_admin_supports = User.objects.filter(groups=ed_admin_support_group)

        context = {
            'fleetowners': fleetowners,
            'fleetowner_supports': fleetowner_supports,
            'ed_admin_supports': ed_admin_supports
        }
        return render(request, 'ed_admin_dashboard.html',  context)
    else:
        return redirect('unauthorized')

@login_required(login_url='login')
def ed_admin_support_dashboard(request):
    if request.user.groups.filter(name='ed_admin_support_person').exists():
        context = {}
        return render(request, 'ed_admin_support_dashboard.html', {'context': context})
    else:
        return redirect('unauthorized')
@login_required(login_url='login')
def fleetowner_dashboard(request):
    if request.user.groups.filter(name='fleetowner').exists():
        return render(request, 'fleetowner_dashboard.html')
    else:
        return redirect('unauthorized')
@login_required(login_url='login')
def fleetowner_support_dashboard(request):
    if request.user.groups.filter(name='fleetowner_support_person').exists():
        # Fetch the fleetowner related to this fleetowner support user
        fleetowner_profile = Profile.objects.filter(user=request.user).first()

        if fleetowner_profile and fleetowner_profile.fleetowner:
            # Get all cars associated with the fleetowner
            cars = Car.objects.filter(owner=fleetowner_profile.fleetowner)

            return render(request, 'fleetowner_support_dashboard.html', {'cars': cars})
        else:
            return redirect('unauthorized')  # If no fleetowner is found in profile
    else:
        return redirect('unauthorized')  # Redirect if the user is not a fleetowner support user


@login_required(login_url='login')
def profile(request):
    username = request.user
    # Fetch user profile data from FleetOwner table based on the logged-in user
    user = User.objects.get(username=username)
    return render(request, 'accounts/profile.html', {'user': user})

@login_required
def profile_update(request):
    if request.method == 'POST':
        # Create forms with POST data and pre-populate with the instance of the user and profile
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect to the profile page after updating
    else:
        # Create empty forms prepopulated with the current user and profile information
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile_update.html', context)


def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('login')

# - Tracker Data
# @login_required(login_url='login')
# def add_tracker_data(request):
#     if request.method == 'GET':
#         # Process incoming GPS tracker data
#         data = parse_gps_tracker_data(request)
#         print("Parsed Data:  ", data)
#         # Enqueue Celery task to process data
#         process_tracker_data.delay(data)
#
#         # Return a response to the tracker acknowledging receipt
#         return HttpResponse("Data received and queued for processing.")
#     else:
#         return HttpResponse("Please check data which is passed")
#
#
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
#         # Check if required fields are present
#         if (registration_number is None or zone is None or vendor is None or auth_key is None or
#                 latitude is None or longitude is None or speed is None or accuracy is None or panic is None or
#                 ignition is None or air_condition is None):
#             raise ValueError("Missing required fields in GPS tracker data")
#
#         # Convert necessary fields to appropriate data types if needed
#         car_registration_number = str(registration_number)
#
#         try:
#             # Check if the car accounts number exists in the Car table
#             car = Car.objects.get(registration_number=car_registration_number)
#         except Car.DoesNotExist:
#             return JsonResponse({'error': 'Car not found'}, status=400)
#
#         # Use filter() instead of get() to handle multiple instances
#         tracker_data_instances = Tracker_data.objects.filter(car=car)
#
#         if tracker_data_instances.exists():
#             # If there are multiple instances, update the first one
#             tracker_data = tracker_data_instances.first()
#         else:
#             # If no instance exists, create a new one
#             tracker_data = Tracker_data(car=car)
#
#         # Update or set the tracker data fields
#         tracker_data.zone = str(zone)
#         tracker_data.vendor = str(vendor)
#         tracker_data.auth_key = str(auth_key)
#         tracker_data.latitude = float(latitude)
#         tracker_data.longitude = float(longitude)
#         tracker_data.speed = float(speed)
#         tracker_data.accuracy = float(accuracy)
#         tracker_data.panic = bool(panic)
#         tracker_data.ignition = bool(ignition)
#         tracker_data.air_condition = float(air_condition)
#
#         # Save the tracker data instance
#         tracker_data.save()
#
#         # Return a dictionary with the extracted data
#         return {
#             'car': car_registration_number,
#             'zone': zone,
#             'vendor': vendor,
#             'auth_key': auth_key,
#             'latitude': float(latitude),
#             'longitude': float(longitude),
#             'speed': float(speed),
#             'accuracy': float(accuracy),
#             'panic': bool(panic),
#             'ignition': bool(ignition),
#             'air_condition': float(air_condition)
#         }
#     except (ValueError, TypeError) as e:
#         # Log or handle the error as needed
#         return JsonResponse({'error': "Invalid GPS tracker data: {}".format(str(e))}, status=400)
#     except Exception as e:
#         # Log or handle other unexpected errors
#         return JsonResponse({'error': "Error processing GPS tracker data: {}".format(str(e))}, status=500)


@login_required(login_url='login')
# @allowed_user(allowed_roles=['fleetowner'])
def tracker_data(request):
    if request.user.groups.filter(name='fleetowner').exists():
        # Retrieve the username of the logged-in user
        username = request.user.username
        # print("Username=============>", username)
        # Attempt to retrieve the FleetOwner based on the username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'error.html', {'message': 'User not found'})

        # Retrieve all cars associated with the FleetOwner
        cars = Car.objects.filter(owner=user)

        # Check if any cars are associated with the FleetOwner
        if not cars.exists():
            return render(request, 'error.html', {'message': 'No cars found for this User'})

        # Create an empty list to store tracker data for all cars
        tracker_data_list = []

        # Loop through each car and retrieve its tracker data
        for car in cars:
            # Retrieve tracker data for the current car
            tracker_data_for_car = Tracker_data.objects.filter(car=car)

            # Extend the tracker_data_list with the tracker data for the current car
            tracker_data_list.extend(tracker_data_for_car)

        context = {'tracker_data_list': tracker_data_list, 'user': user}
        return render(request, 'dashboard.html', context)
    else:
        return redirect('unauthorized')



@login_required(login_url='login')
def tracker_data1(request):
    # tracker_data_list = Tracker_data.objects.all()
    # Retrieve the username of the logged-in user
    username = request.user.username
    print("Username=============>", username)

    # Attempt to retrieve the FleetOwner based on the username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'error.html', {'message': 'User not found'})

    # Retrieve all cars associated with the FleetOwner
    cars = Car.objects.filter(owner=user)

    # Check if any cars are associated with the FleetOwner
    if not cars.exists():
        return render(request, 'error.html', {'message': 'No cars found for this User'})

    # Create an empty list to store tracker data for all cars
    tracker_data_list = []

    # Loop through each car and retrieve its tracker data
    for car in cars:
        # Retrieve tracker data for the current car
        tracker_data_for_car = Tracker_data.objects.filter(car=car)

        # Extend the tracker_data_list with the tracker data for the current car
        tracker_data_list.extend(tracker_data_for_car)

    context = {'tracker_data_list': tracker_data_list, 'user': user}
    return render(request, 'dashboard1.html', context={'tracker_data_list': tracker_data_list})

# - Add Car

# @login_required(login_url='login')
# def add_car(request):
#     if request.method == 'POST':
#         form = CarForm(request.POST)
#         if form.is_valid():
#             car = form.save(commit=False)
#             car.owner = request.user
#             # Check if a tracker with the provided serial number exists
#             tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
#             if tracker_serial_number:
#                 tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
#                 car.tracker = tracker
#
#             car.save()
#             messages.success(request, 'Car added successfully.')  # Add success message
#             return redirect('car_list')  # Adjust the URL name based on your setup
#         else:
#             messages.error(request, 'Failed to add car. Please check the form.')  # Add error message
#     else:
#         form = CarForm()
#
#     return render(request, 'add_car.html', {'form': form})

# @login_required(login_url='login')
# def add_car(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         if request.method == 'POST':
#             form = CarForm(request.POST)
#             if form.is_valid():
#                 car = form.save(commit=False)
#                 car.owner_id = request.user.id  # Assign the logged-in user to the car
#
#                 # Check if a tracker with the provided serial number exists
#                 tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
#                 if tracker_serial_number:
#                     tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
#                     car.tracker = tracker
#
#                 car.save()
#                 messages.success(request, 'Car added successfully.')
#                 return redirect('car_list')  # Adjust the URL name based on your setup
#             else:
#                 messages.error(request, 'Failed to add car. Please check the form.')
#         else:
#             form = CarForm()
#
#         return render(request, 'car_list.html', {'form': form, 'user': request.user})  # Pass the user to the template
#     else:
#         return redirect('unauthorized')
#
#
# # - Car List
# @login_required(login_url='login')
# def car_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # car_list = Car.objects.all()
#         car_list = Car.objects.filter(owner=request.user)
#         return render(request, 'car_list.html', context={'car_list': car_list})
#     else:
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def add_car_and_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Handle form submission (POST request)
#         if request.method == 'POST':
#             form = CarForm(request.POST)
#             if form.is_valid():
#                 car = form.save(commit=False)
#                 car.owner_id = request.user.id  # Assign the logged-in user to the car
#
#                 # Check if a tracker with the provided serial number exists
#                 tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
#                 if tracker_serial_number:
#                     tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
#                     car.tracker = tracker
#
#                 car.save()
#                 messages.success(request, 'Car added successfully.')
#                 return redirect('add_car_and_list')  # Redirect to the same view after successful form submission
#             else:
#                 messages.error(request, 'Failed to add car. Please check the form.')
#                 form = CarForm()
#         else:
#             form = CarForm()
#
#         # Retrieve the list of cars for the logged-in user
#         car_list = Car.objects.filter(owner=request.user)
#
#         # Render the template with both the form and the list of cars
#         return render(request, 'car_list.html', {'form': form, 'car_list': car_list, 'user': request.user})
#     else:
#         return redirect('unauthorized')


# @login_required(login_url='login')
# def add_car_and_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#
#         # Handle form submission (POST request)
#         if request.method == 'POST':
#             if 'car_id' in request.POST:  # Check if car_id is provided to determine update
#                 car = Car.objects.get(id=request.POST['car_id'], owner=request.user)
#                 print("Car============>", car)
#                 form = CarForm(request.POST, instance=car)
#                 if form.is_valid():
#                     car = form.save(commit=False)
#                     car.owner_id = request.user.id  # Assign the logged-in user to the car
#                     print("Car Owner Id=========>", car.owner_id)
#
#                     tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
#                     if tracker_serial_number:
#                         tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
#                         car.tracker = tracker
#
#                     car.save()
#                     messages.success(request, 'Car updated successfully.')
#                     return redirect('add_car_and_list')
#                 else:
#                     messages.error(request, 'Failed to update car. Please check the form.')
#             else:
#                 form = CarForm(request.POST)
#                 if form.is_valid():
#                     car = form.save(commit=False)
#                     car.owner_id = request.user.id
#
#                     tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
#                     if tracker_serial_number:
#                         tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
#                         car.tracker = tracker
#
#                     car.save()
#                     messages.success(request, 'Car added successfully.')
#                     return redirect('add_car_and_list')
#                 else:
#                     messages.error(request, 'Failed to add car. Please check the form.')
#         else:
#             form = CarForm()
#
#         # Retrieve the list of cars for the logged-in user
#         car_list = Car.objects.filter(owner=request.user)
#
#         # Render the template with both the form and the list of cars
#         return render(request, 'car_list.html', {'form': form, 'car_list': car_list, 'user': request.user})
#     else:
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def add_car_and_list(request, car_id=None):  # Assume you're passing `car_id` for updating a specific car
#     if request.user.groups.filter(name='fleetowner').exists():
#         # If car_id is provided, it means we are updating a car; otherwise, it's a new car
#         if car_id:
#             car = get_object_or_404(Car, id=car_id, owner=request.user)  # Fetch the car to be updated
#         else:
#             car = None
#
#         if request.method == 'POST':
#             # If car exists (update), pass the instance; else, create a new one
#             form = CarForm(request.POST, instance=car)
#             if form.is_valid():
#                 car = form.save(commit=False)
#                 car.owner = request.user  # Assign the logged-in user as the car owner
#
#                 # Handle tracker serial number (if provided)
#                 tracker_serial_number = form.cleaned_data.get('tracker_serial_number')
#                 if tracker_serial_number:
#                     tracker, created = GPSTracker.objects.get_or_create(serial_number=tracker_serial_number)
#                     car.tracker = tracker
#
#                 car.save()
#                 messages.success(request, 'Car updated successfully.' if car else 'Car added successfully.')
#                 return redirect('add_car_and_list')  # Redirect after successful submission
#             else:
#                 # Print and handle form errors
#                 print(form.errors)
#                 messages.error(request, 'Failed to update car. Please check the form.')
#         else:
#             # If it's a GET request, populate the form with existing car data if updating
#             form = CarForm(instance=car)
#
#         # Retrieve the list of cars for the logged-in user
#         car_list = Car.objects.filter(owner=request.user)
#
#         # Render the template with the form and car list
#         return render(request, 'car_list.html', {'form': form, 'car_list': car_list, 'user': request.user})
#     else:
#         return redirect('unauthorized')


# @login_required(login_url='login')
# def add_car_and_list(request, car_id=None):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Fetch the car if it's an update, or set to None if adding a new car
#         car = get_object_or_404(Car, id=car_id, owner=request.user) if car_id else None
#
#         if request.method == 'POST':
#             form = CarForm(request.POST, instance=car)
#             if form.is_valid():
#                 try:
#                     # Save the form but don't commit to the database yet
#                     car = form.save(commit=False)
#                     car.owner = request.user
#
#                     # Get the tracker from cleaned data
#                     tracker = form.cleaned_data.get('tracker')
#                     if tracker:
#                         car.tracker = tracker
#
#                     # Check if registration number, chassis number, or tracker are already used by another car
#                     if Car.objects.exclude(id=car_id).filter(registration_number=car.registration_number).exists():
#                         messages.error(request, 'Car with this Registration Number already exists.')
#                     elif Car.objects.exclude(id=car_id).filter(chassis_number=car.chassis_number).exists():
#                         messages.error(request, 'Car with this Chassis Number already exists.')
#                     elif Car.objects.exclude(id=car_id).filter(tracker=car.tracker).exists():
#                         messages.error(request, 'Car with this Tracker already exists.')
#                     else:
#                         # Save the car if there are no duplicates
#                         car.save()
#                         messages.success(request, 'Car updated successfully.' if car_id else 'Car added successfully.')
#                         return redirect('add_car_and_list')
#
#                 except IntegrityError as e:
#                     # Handle other possible database errors
#                     messages.error(request, 'Database error occurred. Please try again.')
#
#             else:
#                 # Handle form validation errors
#                 messages.error(request, 'Failed to update car. Please check the form.')
#                 print(form.errors)
#
#         # Initialize the form if not a POST request
#         form = CarForm(instance=car)
#
#         # Fetch the list of cars for the user
#         car_list = Car.objects.filter(owner=request.user)
#
#         return render(request, 'car_list.html', {'form': form, 'car_list': car_list, 'user': request.user})
#
#     else:
#         return redirect('unauthorized')



@login_required(login_url='login')
def add_car_and_list(request, car_id=None):
    if request.user.groups.filter(name='fleetowner').exists():
        # Fetch the car if it's an update, or set to None if adding a new car
        car = get_object_or_404(Car, id=car_id, owner=request.user) if car_id else None

        if request.method == 'POST':
            form = CarForm(request.POST, instance=car)
            if form.is_valid():
                try:
                    # Save the form but don't commit to the database yet
                    car = form.save(commit=False)
                    car.owner = request.user

                    # Get the tracker from cleaned data
                    tracker = form.cleaned_data.get('tracker')
                    if tracker:
                        car.tracker = tracker

                    # Check if registration number, chassis number, or tracker are already used by another car
                    if Car.objects.exclude(id=car_id).filter(registration_number=car.registration_number).exists():
                        messages.error(request, 'Car with this Registration Number already exists.')
                    elif Car.objects.exclude(id=car_id).filter(chassis_number=car.chassis_number).exists():
                        messages.error(request, 'Car with this Chassis Number already exists.')
                    elif Car.objects.exclude(id=car_id).filter(tracker=car.tracker).exists():
                        messages.error(request, 'Car with this Tracker already exists.')
                    else:
                        # Save the car if there are no duplicates
                        car.save()
                        messages.success(request, 'Car updated successfully.' if car_id else 'Car added successfully.')
                        return redirect('add_car_and_list')

                except IntegrityError as e:
                    # Handle other possible database errors
                    messages.error(request, 'Database error occurred. Please try again.')

            else:
                # Handle form validation errors
                messages.error(request, 'Failed to update car. Please check the form.')
                print(form.errors)

        # Initialize the form if not a POST request
        form = CarForm(instance=car)

        # Fetch the list of cars for the user
        car_list = Car.objects.filter(owner=request.user)

        return render(request, 'car_list.html', {'form': form, 'car_list': car_list, 'user': request.user})

    else:
        return redirect('unauthorized')


# Update Car
@login_required(login_url='login')
def update_car(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        car = get_object_or_404(Car, pk=id)
        if request.method == 'POST':
            form = CarForm(request.POST, instance=car)
            if form.is_valid():
                form.save()
                messages.success(request, 'Car Updated successfully.')  # Add success message
                return redirect('add_car_and_list')  # Adjust the URL name based on your setup
                # return render(request, 'car_list.html')  # Adjust the URL name based on your setup
            else:
                messages.error(request, 'Failed to Update Car. Please check the form.')  # Add error message
        else:
            form = CarForm(instance=car)
        return render(request, 'update_car.html', {'form': form, 'car': car})
    else:
        return redirect('unauthorized')


# Delete Car
@login_required(login_url='login')
def delete_car(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        car = get_object_or_404(Car, id=id, owner=request.user)  # Ensure car belongs to logged-in user
        # print("Car============>", car)
        if request.method == 'POST':
            car.delete()
            messages.success(request, 'Car deleted successfully.')
            return redirect('add_car_and_list')  # Redirect to car list after deletion
        else:
            messages.error(request, 'Failed to Delete Car. Please check the form.')

        return render(request, 'delete_car_confirm.html', {'car': car})
    else:
        return redirect('unauthorized')
# - Add Driver
# @login_required(login_url='login')
# def add_driver(request):
#     if request.method == 'POST':
#         form = DriverForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Driver added successfully.')  # Add success message
#             return redirect('driver_list')
#         else:
#             messages.error(request, 'Failed to add Driver. Please check the form.')  # Add error message
#             form = DriverForm()
#             return redirect('add_driver', {'form': form})
#     else:
#         form = DriverForm()
#         return render(request, 'add_driver.html', {'form': form})

# @login_required(login_url='login')
# def add_driver(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         car = Car.objects.get(owner_id=request.user.id)  # Ensure the car belongs to the logged-in user
#         if request.method == 'POST':
#             form = DriverForm(request.POST, request.FILES)
#             if form.is_valid():
#                 driver = form.save(commit=False)
#                 driver.car = car  # Associate the driver with the car
#                 driver.save()
#                 messages.success(request, 'Driver added successfully.')
#                 return redirect('driver_list')  # Adjust based on your setup
#             else:
#                 messages.error(request, 'Failed to add driver. Please check the form.')
#         else:
#             form = DriverForm()
#         return render(request, 'add_driver.html', {'form': form, 'car': car})
#     else:
#         return redirect('unauthorized')
#
#
# @login_required(login_url='login')
# def driver_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         cars = Car.objects.filter(owner=request.user)  # Get all cars for the logged-in user
#         print(f"Cars for {request.user}", cars)
#         drivers_list = Driver.objects.filter(car__in=cars)  # Get drivers associated with those cars
#         print("Drivers_list=============>", drivers_list)
#         return render(request, 'driver_list.html', {'drivers_list': drivers_list})
#     else:
#         return redirect('unauthorized')

@login_required(login_url='login')
def add_driver_and_list(request):
    if request.user.groups.filter(name='fleetowner').exists():
        cars = Car.objects.filter(owner=request.user)  # Get all cars for the logged-in user
        drivers_list = Driver.objects.filter(car__in=cars)  # Get drivers associated with those cars

        if request.method == 'POST':
            form = DriverForm(request.POST, request.FILES)
            if form.is_valid():
                driver = form.save(commit=False)
                car = cars.first()  # Assuming the fleetowner has only one car, adjust if needed
                driver.car = car
                driver.save()
                messages.success(request, 'Driver added successfully.')
                return redirect('add_driver_and_list')  # Redirect to the same page to show the updated list
            else:
                messages.error(request, 'Failed to add driver. Please check the form.')
        else:
            form = DriverForm()

        # Render the template with both the form and the list of drivers
        return render(request, 'driver_list.html', {'form': form, 'drivers_list': drivers_list, 'cars': cars})
    else:
        return redirect('unauthorized')

@login_required(login_url='login')
def update_driver(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        driver = get_object_or_404(Driver, pk=id)
        if request.method == 'POST':
            form = DriverForm(request.POST, request.FILES, instance=driver)
            if form.is_valid():
                form.save()
                messages.success(request, 'Driver Updated successfully.')  # Add success message
                return redirect('add_driver_and_list')  # Adjust the URL name based on your setup
            else:
                # messages.error(request, 'Failed to Update Driver. Please check the form.')  # Add error message
                messages.error(request, f'Failed to Update Driver. Errors: {form.errors}')  # Add error message
        else:
            form = DriverForm(instance=driver)
        return render(request, 'update_driver.html', {'form': form, 'driver': driver})
    else:
        return redirect('unauthorized')

@login_required(login_url='login')
def delete_driver(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        driver = get_object_or_404(Driver, id=id)
        if request.method == 'POST':
            driver.delete()
            messages.success(request, 'Driver Deleted successfully.')  # Add success message
            return redirect('driver_list')  # Replace with your actual driver list URL name
        else:
            messages.error(request, 'Failed to Delete Driver. Please check the form.')  # Add error message

        return render(request, 'delete_driver.html', {'driver': driver})
    else:
        return redirect('unauthorized')



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
# @login_required(login_url='login')
# def add_tracker(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         if request.method == 'POST':
#             form = TrackerForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 return JsonResponse({'success': True})
#             else:
#                 errors = form.errors.as_json()
#                 return JsonResponse({'success': False, 'errors': errors})
#         else:
#             form = TrackerForm()
#         return render(request, 'add_tracker.html', {'form': form})
#     else:
#         return redirect('unauthorized')
#
#
# # - Tracker List
# @login_required(login_url='login')
# def tracker_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Get all cars owned by the logged-in user
#         cars = Car.objects.filter(owner=request.user)
#         # print(f"Cars for {request.user}", cars)
#         # Get all trackers associated with those cars
#         tracker_list = GPSTracker.objects.filter(car__in=cars)
#         # print("Trackers========> ", tracker_list)
#         return render(request, 'tracker_list.html', {'tracker_list': tracker_list})
#     else:
#         return redirect('unauthorized')


# @login_required(login_url='login')
# def add_tracker_and_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Get all cars owned by the logged-in user
#         cars = Car.objects.filter(owner=request.user)
#         # Get all trackers associated with those cars
#         tracker_list = GPSTracker.objects.filter(car__in=cars)
#         # Get all trackers added by the logged-in user
#         # tracker_list = GPSTracker.objects.filter(added_by=request.user)
#
#         if request.method == 'POST':
#             form = TrackerForm(request.POST)
#             if form.is_valid():
#                 tracker = form.save(commit=False)
#                 tracker.car = cars.first()  # Assuming the fleetowner has only one car, adjust if needed
#                 # tracker.added_by = request.user  # Assign the logged-in user as the one who added the tracker
#                 tracker.save()
#                 messages.success(request, 'Tracker added successfully.')
#                 return redirect('add_tracker_and_list')
#             else:
#                 messages.error(request, 'Tracker is not added successfully.')
#                 return redirect('add_tracker_and_list')
#         else:
#             form = TrackerForm()
#
#         # Render the form and tracker list in the same template
#         return render(request, 'tracker_list.html', {
#             'form': form,
#             'tracker_list': tracker_list,
#             'cars': cars
#         })
#     else:
#         return redirect

@login_required(login_url='login')
def add_tracker_and_list(request):
    if request.user.groups.filter(name='fleetowner').exists():
        # Get all cars owned by the logged-in user
        cars = Car.objects.filter(owner=request.user)

        # Get all trackers added by the logged-in user
        tracker_list = GPSTracker.objects.filter(added_by=request.user)

        if request.method == 'POST':
            form = TrackerForm(request.POST)
            if form.is_valid():
                tracker = form.save(commit=False)
                tracker.car = cars.first()  # Assuming the fleetowner has only one car, adjust if needed
                tracker.added_by = request.user  # Assign the logged-in user as the one who added the tracker
                tracker.save()
                messages.success(request, 'Tracker added successfully.')
                return redirect('add_tracker_and_list')
            else:
                messages.error(request, 'Tracker is not added successfully.')
                return redirect('add_tracker_and_list')
        else:
            form = TrackerForm()

        # Render the form and tracker list in the same template
        return render(request, 'tracker_list.html', {
            'form': form,
            'tracker_list': tracker_list,
            'cars': cars
        })
    else:
        return redirect('unauthorized')


@login_required(login_url='login')
def update_tracker(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        tracker = get_object_or_404(GPSTracker, id=id)
        # Ensure that the tracker belongs to the logged-in user (either by car ownership or added_by)
        if not (tracker.added_by == request.user):
            messages.error(request, 'You are not authorized to update this tracker.')
            # return redirect('add_tracker_and_list')  # Redirect if the user is not authorized
            return render(request, 'update_tracker.html', )
        if request.method == 'POST':
            form = TrackerForm(request.POST, instance=tracker)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tracker Updated successfully.')  # Add success message
                return redirect('add_tracker_and_list')  # Adjust the URL name based on your setup
            else:
                messages.error(request, 'Failed to Update Tracker. Please check the form.')  # Add error message
        else:
            form = TrackerForm(instance=tracker)
        return render(request, 'update_tracker.html', {'form': form, 'tracker': tracker})
    else:
        return redirect('unauthorized')

@login_required(login_url='login')
def delete_tracker(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        tracker = get_object_or_404(GPSTracker, id=id)
        if request.method == 'POST':
            tracker.delete()
            messages.success(request, 'Tracker Deleted successfully.')  # Add success message
            return redirect('add_tracker_and_list')  # Replace with your actual tracker list URL name
        else:
            messages.error(request, 'Failed to Delete Tracker. Please check the form.')  # Add error message

        return render(request, 'delete_tracker.html', {'tracker': tracker})
    else:
        return redirect('unauthorized')

# - Add RFID
# @login_required(login_url='login')
# def add_rfid(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         if request.method == 'POST':
#             form = RFIDForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 return redirect('rfid_list')  # Redirect to a view that displays the list of RFIDs
#         else:
#             form = RFIDForm()
#
#         return render(request, 'add_rfid.html', {'form': form})
#     else:
#         return redirect('unauthorized')
#
# # - RFID List
# # @login_required(login_url='login')
# # def rfid_list(request):
# #     rfid_list = RFID.objects.all()
# #     return render(request, 'rfid_list.html', {'rfid_list': rfid_list})
#
# @login_required(login_url='login')
# def rfid_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Get all cars owned by the logged-in user
#         cars = Car.objects.filter(owner=request.user)
#
#         # Get all drivers associated with those cars
#         drivers = Driver.objects.filter(car__in=cars)
#
#         # Get all RFIDs associated with those drivers
#         rfid_list = RFID.objects.filter(driver__in=drivers)
#
#         return render(request, 'rfid_list.html', {'rfid_list': rfid_list})
#     else:
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def add_rfid_and_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#
#         # Handle the POST request (form submission)
#         if request.method == 'POST':
#             form = RFIDForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'You have added rfid successfully')
#                 return redirect('add_rfid_and_list')  # Redirect to the same view after adding RFID to refresh the list
#         else:
#             form = RFIDForm()
#         # Get all cars owned by the logged-in user
#         cars = Car.objects.filter(owner=request.user)
#
#         # Get all drivers associated with those cars
#         drivers = Driver.objects.filter(car__in=cars)
#
#         # Get all RFIDs associated with those drivers
#         rfid_list = RFID.objects.filter(driver__in=drivers)
#         return render(request, 'rfid_list.html', {'form': form, 'rfid_list': rfid_list})
#
#     else:
#         return redirect('unauthorized')
@login_required(login_url='login')
def add_rfid_and_list(request):
    if request.user.groups.filter(name='fleetowner').exists():

        # Handle the POST request (form submission)
        if request.method == 'POST':
            form = RFIDForm(request.POST)
            if form.is_valid():
                rfid = form.save(commit=False)
                rfid.added_by = request.user  # Assuming you have a field 'added_by' in RFID model
                rfid.save()
                messages.success(request, 'You have added rfid successfully')
                return redirect('add_rfid_and_list')  # Redirect to the same view after adding RFID to refresh the list
        else:
            form = RFIDForm()

        # Get all cars owned by the logged-in user
        cars = Car.objects.filter(owner=request.user)

        # Get all drivers associated with those cars
        drivers = Driver.objects.filter(car__in=cars)

        # Get all RFIDs added by the logged-in user, associated or not
        rfid_list = RFID.objects.filter(added_by=request.user)  # Assuming RFID model has 'added_by' field

        return render(request, 'rfid_list.html', {'form': form, 'rfid_list': rfid_list})

    else:
        return redirect('unauthorized')


@login_required(login_url='login')
def update_rfid(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        rfid = get_object_or_404(RFID, pk=id)
        if request.method == 'POST':
            form = RFIDForm(request.POST, instance=rfid)
            if form.is_valid():
                form.save()
                messages.success(request, 'RFID updated successfully!')
                return redirect('add_rfid_and_list')  # Adjust the URL name based on your setup
            else:
                messages.error(request, 'RFID not updated successfully!')
        else:
            form = RFIDForm(instance=rfid)
        return render(request, 'update_rfid.html', {'form': form, 'rfid': rfid})
    else:
        return redirect('unauthorized')

@login_required(login_url='login')
def delete_rfid(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        rfid = get_object_or_404(RFID, id=id)
        if request.method == 'POST':
            rfid.delete()
            messages.success(request, 'RFID deleted successfully!')
            return redirect('add_rfid_and_list')  # Replace with your actual rfid list URL name
        else:
            messages.error(request, 'Failed to Delete RFID. Please check the form.')

        return render(request, 'delete_rfid.html', {'rfid': rfid})
    else:
        return redirect('unauthorized')





# Cron Job or Periodic Task
def send_tracker_data_periodically():
    while True:
        send_tracker_data_to_api(None)  # Sending tracker data
        time.sleep(10)  # Wait for 10 seconds before sending the next update


# Add fleetowner_support user
# @login_required(login_url='login')
# def add_fleetowner_support_user(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         if request.method == 'POST':
#             form = FleetOwnerSupportUserForm(request.POST)
#             if form.is_valid():
#                 # Save the form with the logged-in fleetowner
#                 form.save(fleetowner=request.user)
#                 messages.success(request, 'You have added Fleetowner Support User successfully!!!')
#                 return redirect('fleetowner_dashboard')
#         else:
#             form = FleetOwnerSupportUserForm()
#             return render(request, 'add_fleetowner_support_user.html', {'form': form})
#     else:
#         return redirect('unauthorized')


@login_required(login_url='login')
def add_fleetowner_support_user(request):
    if request.user.groups.filter(name='fleetowner').exists():
        if request.method == 'POST':
            form = FleetOwnerSupportUserForm(request.POST)
            if form.is_valid():
                # Create the user first
                support_user = form.save(fleetowner=request.user)
                print("Support User================>", support_user)

                # Then create the profile with the fleetowner field
                Profile.objects.create(
                    user=support_user,
                    fleetowner=request.user,
                    address1=form.cleaned_data['address1'],
                    address2=form.cleaned_data['address2'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    pin=form.cleaned_data['pin'],
                    country=form.cleaned_data['country'],
                    mobile=form.cleaned_data['mobile']
                )

                messages.success(request, 'You have added Fleetowner Support User successfully!')
                return redirect('fleetowner_dashboard')
        else:
            form = FleetOwnerSupportUserForm()

        return render(request, 'add_fleetowner_support_user.html', {'form': form})
    else:
        return redirect('unauthorized')



# Edit fleetowner_support user
# @login_required(login_url='login')
# def edit_fleetowner_support_user(request, id):
#     if request.user.groups.filter(name='fleetowner').exists():
#         user = get_object_or_404(User, id=id)
#         print("User at edit", user)
#         if request.method == 'POST':
#
#             form = FleetOwnerSupportUserForm(request.POST, instance=user)
#             if form.is_valid():
#                 form.save(fleetowner=request.user)
#                 messages.success(request, f'You have updated {user} successfully.')
#                 return redirect('fleetowner_dashboard')
#         else:
#             form = FleetOwnerSupportUserForm(instance=user)
#         return render(request, 'edit_fleetowner_support_user.html', {'form': form})
#     else:
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def edit_fleetowner_support_user(request, id):
#     # Ensure the user is a fleetowner
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Get the support user by ID
#         support_user = get_object_or_404(User, id=id)
#         print("Support User ==============>", support_user)
#
#         if request.method == 'POST':
#             form = FleetOwnerSupportUserForm(request.POST, instance=support_user)
#             if form.is_valid():
#                 form.save(fleetowner=request.user)
#                 messages.success(request, f'You have updated {support_user.username} successfully.')
#                 return redirect('fleetowner_support_list')  # Redirect to the list page
#         else:
#             form = FleetOwnerSupportUserForm(instance=support_user)
#
#         return render(request, 'edit_fleetowner_support_user.html', {'form': form, 'support_user': support_user})
#
#     else:
#         messages.error(request, "You are not authorized to edit this user.")
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def edit_fleetowner_support_user(request, id):
#     # Ensure the logged-in user is a fleetowner
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Fetch the support user by ID and check that the support user belongs to the current fleetowner
#         support_user = get_object_or_404(User, id=id, profile__fleetowner=request.user)
#
#         if request.method == 'POST':
#             form = FleetOwnerSupportUserForm(request.POST, instance=support_user)
#             if form.is_valid():
#                 form.save()  # No need to pass fleetowner, as we're editing an existing user
#                 messages.success(request, 'Fleetowner Support User updated successfully.')
#                 return redirect('fleetowner_dashboard')
#         else:
#             form = FleetOwnerSupportUserForm(instance=support_user)
#
#         return render(request, 'edit_fleetowner_support_user.html', {'form': form})
#     else:
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def edit_fleetowner_support_user(request, id):
#     # Ensure the logged-in user is a fleetowner
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Get the support user by ID
#         support_user = get_object_or_404(User, id=id)
#
#         # Check if the support user's profile is linked to the logged-in fleetowner
#         if support_user.profile.fleetowner != request.user:
#             messages.error(request, 'You are not authorized to edit this user.')
#             return redirect('fleetowner_dashboard')
#
#         # Handle form submission
#         if request.method == 'POST':
#             form = FleetOwnerSupportUserForm(request.POST, instance=support_user)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'Fleetowner Support User updated successfully.')
#                 return redirect('fleetowner_dashboard')
#         else:
#             form = FleetOwnerSupportUserForm(instance=support_user)
#
#         return render(request, 'edit_fleetowner_support_user.html', {'form': form})
#     else:
#         return redirect('unauthorized')

# @login_required(login_url='login')
# def edit_fleetowner_support_user(request, id):
#     support_user = get_object_or_404(User, id=id)
#
#     # Check if the logged-in fleetowner is the one associated with the fleetowner_support user
#     if request.user.groups.filter(name='fleetowner').exists() and request.user == support_user.profile.fleetowner:
#         if request.method == 'POST':
#             form = FleetOwnerSupportUserForm(request.POST, instance=support_user)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, f'You have updated {support_user.username} successfully.')
#                 return redirect('fleetowner_dashboard')
#         else:
#             form = FleetOwnerSupportUserForm(instance=support_user)
#         return render(request, 'edit_fleetowner_support_user.html', {'form': form})
#     else:
#         messages.error(request, 'You are not authorized to edit this user.')
#         return redirect('unauthorized')

@login_required(login_url='login')
def edit_fleetowner_support_user(request, id):
    try:
        # Get the user by ID
        support_user = get_object_or_404(FleetOwnerSupport, id=id)

        if request.method == 'POST':
            form = FleetOwnerSupportUserForm(request.POST, instance=support_user)
            if form.is_valid():
                form.save()
                messages.success(request, f'You have updated {support_user.username} successfully.')
                return redirect('fleetowner_dashboard')
        else:
            form = FleetOwnerSupportUserForm(instance=support_user)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('fleetowner_dashboard')

    return render(request, 'edit_fleetowner_support_user.html', {'form': form})



# Delete fleetowner_support user
@login_required(login_url='login')
def delete_fleetowner_support_user(request, id):
    if request.user.groups.filter(name='fleetowner').exists():
        user = get_object_or_404(FleetOwnerSupport, id=id)
        if request.method == 'POST':
            user.delete()
            messages.success(request, 'You have delete user successfully!!!')
            return redirect('fleetowner_dashboard')

        return render(request, 'delete_fleetowner_support_user.html', {'user': user})
    else:
        return redirect('unauthorized')

# @login_required
# def delete_fleetowner_support_user(request, id):
#     if request.user.groups.filter(name='fleetowner').exists():
#         user = get_object_or_404(User, id=id)
#
#         # Ensure the support user belongs to the logged-in fleetowner
#         if user.profile.fleetowner != request.user:
#             messages.error(request, 'You are not authorized to delete this user.')
#             return redirect('fleetowner_dashboard')
#
#         if request.method == 'POST':
#             user.delete()
#             messages.success(request, 'You have deleted the support user successfully.')
#             return redirect('fleetowner_dashboard')  # 200
#
#         return render(request, 'delete_fleetowner_support_user.html', {'user': user})
#     else:
#         return redirect('unauthorized')  # 302

# @login_required(login_url='login')
# def delete_fleetowner_support_user(request, id):
#     if request.user.groups.filter(name='fleetowner').exists():
#         support_user = get_object_or_404(Profile, id=id, fleetowner=request.user)
#         if request.method == 'POST':
#             support_user.user.delete()
#             messages.success(request, 'Support user deleted successfully!')
#             return redirect('fleetowner_dashboard')
#
#         return render(request, 'delete_fleetowner_support_user.html', {'support_user': support_user})
#     else:
#         return redirect('unauthorized')


# @login_required
# def fleetowner_support_user_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         support_users = User.objects.filter(groups__name='fleetowner_support_person')
#         return render(request, 'fleetowner_support_user_list.html', {'support_users': support_users})
#     else:
#         return redirect('unauthorized')


# @login_required
# def fleetowner_support_user_list(request):
#     if request.user.groups.filter(name='fleetowner').exists():
#         # Get the list of support users for the logged-in fleetowner
#         support_users = FleetOwnerSupport.objects.filter(fleetowner=request.user).select_related('fleetowner_support_user')
#         print("Support Users QuerySet==============>", support_users)
#         for support_user in support_users:
#             print(" Support User======>", support_user)
#         return render(request, 'fleetowner_support_user_list.html', {'support_users': support_users})
#     else:
#         return redirect('unauthorized')


@login_required(login_url='login')
def fleetowner_support_user_list(request):
    # Get the fleetowner support users for the logged-in fleetowner
    support_users = FleetOwnerSupport.objects.filter(fleetowner=request.user)  # Adjust as per your model
    for users in support_users:
        print("Fleetowner support User List", users.id)

    return render(request, 'fleetowner_support_user_list.html', {'support_users': support_users})


@login_required(login_url='login')
def unauthorized(request):
    return render(request, 'unauthorized.html')


@login_required(login_url='login')
def fleetowner_support_user_cars(request):
    if request.user.groups.filter(name='fleetowner_support_person').exists():
        # Fetch the fleetowner related to this fleetowner support user
        fleetowner_profile = Profile.objects.filter(user=request.user).first()

        if fleetowner_profile and fleetowner_profile.fleetowner:
            # Get all cars associated with the fleetowner
            cars = Car.objects.filter(owner=fleetowner_profile.fleetowner)

            return render(request, 'fleetowner_support_dashboard.html', {'cars': cars})
        else:
            return redirect('unauthorized')  # If no fleetowner is found in profile
    else:
        return redirect('unauthorized')  # Redirect if the user is not a fleetowner support user