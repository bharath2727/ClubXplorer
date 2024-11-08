from django.contrib import admin
from .models import User, Ground, Booking, Event

# Optional: To customize the admin interface


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_user')
    search_fields = ('username', 'email')


class GroundAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_description', 'availability_status')
    search_fields = ('name',)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'ground', 'date', 'time_slot')
    list_filter = ('date', 'ground')
    search_fields = ('user__username', 'ground__name')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'date',
                    'time', 'ground', 'organized_by')
    list_filter = ('date', 'ground')
    search_fields = ('name', 'ground__name', 'organized_by__username')


# Registering models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Ground, GroundAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Event, EventAdmin)
