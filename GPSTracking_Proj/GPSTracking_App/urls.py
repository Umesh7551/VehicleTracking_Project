from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.register, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.user_login, name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('accounts/profile/', views.profile, name='profile'),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('tracker_data/', views.tracker_data, name='tracker_data'),
    path('tracker_data1/', views.tracker_data1, name='tracker_data1'),
    # path('add_car/', views.add_car, name='add_car'),
    # path('car_list/', views.car_list, name='car_list'),
    path('add_car_and_list/', views.add_car_and_list, name='add_car_and_list'),
    path('update_car/<int:id>/', views.update_car, name='update_car'),
    path('delete_car/<int:id>/', views.delete_car, name='delete_car'),
    # path('add_driver/', views.add_driver, name='add_driver'),
    path('add_driver_and_list/', views.add_driver_and_list, name='add_driver_and_list'),
    # path('driver_list/', views.driver_list, name='driver_list'),
    path('update_driver/<int:id>/', views.update_driver, name='update_driver'),
    path('delete_driver/<int:id>/', views.delete_driver, name='delete_driver'),
    path('add_tracker_and_list/', views.add_tracker_and_list, name='add_tracker_and_list'),
    # path('tracker_list/', views.tracker_list, name='tracker_list'),
    path('update_tracker/<int:id>/', views.update_tracker, name='update_tracker'),
    path('delete_tracker/<int:id>/', views.delete_tracker, name='delete_tracker'),
    path('add_rfid_and_list/', views.add_rfid_and_list, name='add_rfid_and_list'),
    # path('add_rfid/', views.add_rfid, name='add_rfid'),
    # path('rfid_list/', views.rfid_list, name='rfid_list'),
    path('update_rfid/<int:id>/', views.update_rfid, name='update_rfid'),
    path('delete_rfid/<int:id>/', views.delete_rfid, name='delete_rfid'),
    path('ed_admin/dashboard/', views.ed_admin_dashboard, name='ed_admin_dashboard'),
    path('ed_admin_support/dashboard/', views.ed_admin_support_dashboard, name='ed_admin_support_dashboard'),
    path('fleetowner_dashboard/', views.fleetowner_dashboard, name='fleetowner_dashboard'),
    path('fleetowner_support/dashboard/', views.fleetowner_support_dashboard, name='fleetowner_support_dashboard'),
    path('password/change/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/change_password_done.html'), name='password_change_done'),
    path('add_support_user/', views.add_fleetowner_support_user, name='add_support_user'),
    path('edit_fleetowner_support_user/<int:id>/', views.edit_fleetowner_support_user, name='edit_fleetowner_support_user'),
    path('delete_fleetowner_support_user/<int:id>/', views.delete_fleetowner_support_user, name='delete_fleetowner_support_user'),
    path('fleetowner_support_user_list/', views.fleetowner_support_user_list, name='fleetowner_support_user_list'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),
    # path('fleetowner-support/cars/', views.fleetowner_support_user_cars, name='fleetowner_support_user_cars'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
