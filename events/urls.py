from django.urls import path
from .views import (
    home, all_events, add_event, redirect_dashboard, event_detail,
    edit_event, delete_event, admin_dashboard, rsvp_event,
    organizer_dashboard, participant_dashboard, users_control_view,
    events_control_view, categories_control_view, 
    edit_profile, attended_events
)

urlpatterns = [
    # Public pages
    path('home/', home, name='home'),
    path('all_events/', all_events, name='all_events'),

    # Dashboard redirect based on user role
    path('dashboard/', redirect_dashboard, name='dashboard'),

    # Event detail and management
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),

    # Admin dashboard routes
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', users_control_view, name='users_control'),

    # Organizer dashboard routes
    path('organizer/dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('organizer/events/control/', events_control_view, name='events_control'),
    path('organizer/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('organizer/<int:event_id>/delete/', delete_event, name='delete_event'),
    path('organizer/categories/control/', categories_control_view, name='categories_control'),
    path('organizer/add_event/', add_event, name='add_event'),
    path('organizer/profile/edit/', edit_profile, name='edit_profile'),

    # Participant dashboard
    path('participant/dashboard/', participant_dashboard, name='participant_dashboard'),
    path("participant/attended-events/", attended_events, name="attended_events"),
]