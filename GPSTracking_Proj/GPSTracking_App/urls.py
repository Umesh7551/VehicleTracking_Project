from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

# from .views import SignUpView

# from .views import FleetOwnerLoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    # path('login/', LoginView.as_view(), name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    # path('signup/', SignUpView.as_view(), name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    path('add_fleet_owner/', views.add_fleet_owner, name='add_fleet_owner'),
    path('fleet_owner_list/', views.fleet_owner_list, name='fleet_owner_list'),
    path('update_fleet_owner/<int:id>/', views.update_fleetowner, name='update_fleetowner'),
    # path('add_tracker_data/', views.add_tracker_data, name='add_tracker_data'),
    # path('tracker_data/<int:id>/', views.tracker_data, name='tracker_data'),
    path('tracker_data/', views.tracker_data, name='tracker_data'),
    path('tracker_data1/', views.tracker_data1, name='tracker_data1'),
    path('add_car/', views.add_car, name='add_car'),
    path('car_list/', views.car_list, name='car_list'),
    path('update_car/<int:id>/', views.update_car, name='update_car'),
    path('add_driver/', views.add_driver, name='add_driver'),
    path('driver_list/', views.driver_list, name='driver_list'),
    path('update_driver/<int:id>/', views.update_driver, name='update_driver'),
    path('delete_driver/<int:id>/', views.delete_driver, name='delete_driver'),
    path('add_tracker/', views.add_tracker, name='add_tracker'),
    path('tracker_list/', views.tracker_list, name='tracker_list'),
    path('add_rfid/', views.add_rfid, name='add_rfid'),
    path('rfid_list/', views.rfid_list, name='rfid_list'),
    path('update_rfid/<int:id>/', views.update_rfid, name='update_rfid'),
    path('delete_rfid/<int:id>/', views.delete_rfid, name='delete_rfid'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)