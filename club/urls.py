from django.urls import path, include
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('password-reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    # Booking URLs
    path('booking/', views.booking_view, name='booking'),
    path('cancel_booking/<int:booking_id>/',
         views.cancel_booking, name='cancel_booking'),
    path('view_bookings/', views.view_booking, name='view_booking'),

    # Event URLs
    # For creating a new event
    path('event/', views.event_view, name='event_create'),
    path('payment_success/', views.payment_success, name='payment_success'),
    # For listing all events
    path('events/', views.view_events, name='view_events'),
    path('events/register/<int:event_id>/',
         views.register_for_event, name='register_for_event'),
    path('events/cancel_registration/<int:registration_id>/',
         views.cancel_event_registration, name='cancel_event_registration'),
    path('activities/bookings/', views.view_bookings, name='view_bookings'),
    path('activities/events/', views.view_event_registrations,
         name='view_event_registrations'),

]
