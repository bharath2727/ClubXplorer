from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


class Ground(models.Model):
    name = models.CharField(max_length=100)
    location_description = models.TextField()
    availability_status = models.BooleanField(
        default=True)  # True if available, False otherwise
    price = models.DecimalField(
        max_digits=8, decimal_places=2)  # Adding price field

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    ground = models.ForeignKey(
        Ground,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    date = models.DateField()
    time_slot = models.CharField(max_length=50)  # Example: "6:00 AM - 7:00 AM"

    def __str__(self):
        return f"{self.ground.name} on {self.date} at {self.time_slot} by {self.user.username}"


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    ground = models.ForeignKey(
        Ground,
        on_delete=models.CASCADE,
        related_name="events"
    )
    organized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name="events"
    )
    promotion_details = models.TextField()

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    event = models.ForeignKey(
        'Event', on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} registered for {self.event.name}"
