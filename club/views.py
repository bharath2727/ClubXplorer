from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordResetView
import json
import re
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import get_user_model
from django.urls import reverse
import stripe
UserModel = get_user_model()

@login_required(login_url='login')
def home(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if len(username) < 6:
            messages.error(
                request, "Username must be at least 6 characters long")
            return redirect('signup')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Invalid email address")
            return redirect('signup')

        if len(password1) < 8:
            messages.error(
                request, "Password must be at least 8 characters long")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if UserModel.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')

        if UserModel.objects.filter(email=email).exists():
            messages.error(request, "Email already taken")
            return redirect('signup')

        user = UserModel.objects.create_user(
            username=username, email=email, password=password1)
        user.save()
        messages.success(request, "User Registeres Successfully")
        return redirect('signup')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')




class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')

def booking(request):
    return render(request, 'booking_form.html')

from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def booking_view(request):
    grounds = Ground.objects.all()
    if request.method == 'POST':
        user = request.user
        ground_id = request.POST.get('ground')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        ground = Ground.objects.get(id=ground_id)

        if Booking.objects.filter(ground=ground, date=date, time_slot=time_slot).exists():
            messages.error(
                request, "This slot is already booked. Please select another slot.")
        else:
            # Create Stripe Checkout Session
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': ground.name,
                            },
                            'unit_amount': int(ground.price * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(
                        reverse('payment_success')),
                    cancel_url=request.build_absolute_uri(reverse('booking')),
                )
                request.session['checkout_session_id'] = checkout_session.id
                request.session['ground_id'] = ground_id
                request.session['date'] = date
                request.session['time_slot'] = time_slot
                # Redirect to Stripe Checkout
                return redirect(checkout_session.url)
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'booking_form.html', {'grounds': grounds})

    # For GET requests
    booked_slots = Booking.objects.filter(
        date__gte=timezone.now()).values_list('date', 'time_slot', named=True)
    booked_slots_list = [{'date': b.date.strftime(
        "%Y-%m-%d"), 'time_slot': b.time_slot} for b in booked_slots]
    booked_slots_json = json.dumps(booked_slots_list)
    return render(request, 'booking_form.html', {'grounds': grounds, 'booked_slots_json': booked_slots_json})


@login_required
def event_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        ground_id = request.POST.get('ground')
        promotion_details = request.POST.get('promotion_details')
        ground = Ground.objects.get(id=ground_id)
        event = Event.objects.create(name=name, description=description, date=date, time=time,
                                     ground=ground, organized_by=request.user, promotion_details=promotion_details)
        event.save()
        messages.success(request, "Event created successfully!")
        return redirect('events')
    else:
        grounds = Ground.objects.all()
        return render(request, 'event_form.html', {'grounds': grounds})


@login_required
def events_list(request):
    events = Event.objects.all()
    return render(request, 'events_list.html', {'events': events})


@login_required
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
        booking.delete()
        messages.success(request, "Booking successfully cancelled.")
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
    return redirect('view_bookings')


def view_booking(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    event_registrations = EventRegistration.objects.filter(
        user=request.user).order_by('event__date')
    return render(request, 'view_bookings.html', {'bookings': bookings, 'event_registrations': event_registrations})

# View for detailed bookings
@login_required
def view_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    return render(request, 'detailed_bookings.html', {'bookings': bookings})

# View for detailed event registrations
@login_required
def view_event_registrations(request):
    event_registrations = EventRegistration.objects.filter(user=request.user).order_by('event__date')
    return render(request, 'detailed_event_registrations.html', {'event_registrations': event_registrations})


@login_required
def view_events(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'view_events.html', {'events': events})


@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    # Check if the user is already registered
    if not EventRegistration.objects.filter(event=event, user=request.user).exists():
        EventRegistration.objects.create(event=event, user=request.user)
        messages.success(
            request, "You have successfully registered for the event.")
    else:
        messages.info(request, "You are already registered for this event.")
    return redirect('view_events')


@login_required
def cancel_event_registration(request, registration_id):
    registration = get_object_or_404(
        EventRegistration, id=registration_id, user=request.user)
    registration.delete()
    messages.success(request, "Event registration cancelled successfully.")
    return redirect('view_event_registrations')


@login_required
def payment_success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session_id = request.session.get('checkout_session_id')

    if not session_id:
        messages.error(request, "No Stripe session found.")
        return redirect('view_bookings')  # Adjust as needed

    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status == "paid":
            # Here, handle your booking logic
            # Example: creating a Booking instance
            # Ensure you have stored enough information to recreate the booking
            ground_id = request.session.get('ground_id')
            date = request.session.get('date')
            time_slot = request.session.get('time_slot')
            ground = get_object_or_404(Ground, id=ground_id)
            Booking.objects.create(
                user=request.user, ground=ground, date=date, time_slot=time_slot)

            # Clear session data
            del request.session['checkout_session_id']
            del request.session['ground_id']
            del request.session['date']
            del request.session['time_slot']
            request.session.modified = True

            return render(request, 'payment_success.html')
        else:
            messages.error(request, "Payment was not successful.")
            return redirect('view_bookings')  # Adjust as needed
    except Exception as e:
        messages.error(request, str(e))
        return redirect('view_bookings')  # Adjust as needed
