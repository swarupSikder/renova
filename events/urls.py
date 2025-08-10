from django.urls import path
from .views import (
    home,
    DashboardView,
    AllEventsView,
    AddEventView,
    redirect_dashboard,
    EventDetailView,
    EditEventView,
    delete_event,
    rsvp_event,
    users_control_view,
    events_control_view,
    categories_control_view,
    edit_profile,
    attended_events,
)

urlpatterns = [
    path('home/', home, name='home'),

    # Events list with filtering
    path('all_events/', AllEventsView.as_view(), name='all_events'),

    # Dashboard root - uses CBV
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Profile edit page - FBV
    path('dashboard/profile/edit/', edit_profile, name='edit_profile'),

    # Event detail and RSVP - detail is CBV, RSVP is FBV
    path('event/<int:event_id>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),

    # Admin user controls - FBV
    path('dashboard/users/', users_control_view, name='users_control'),

    # Organizer event controls
    path('dashboard/events/control/', events_control_view, name='events_control'),
    path('dashboard/add_event/', AddEventView.as_view(), name='add_event'),          # CBV for adding event
    path('dashboard/<int:event_id>/edit/', EditEventView.as_view(), name='edit_event'),  # CBV for editing event
    path('dashboard/<int:event_id>/delete/', delete_event, name='delete_event'),     # FBV for deleting event
    path('dashboard/categories/control/', categories_control_view, name='categories_control'),

    # Participant attended events - FBV
    path('dashboard/attended-events/', attended_events, name='attended_events'),
]