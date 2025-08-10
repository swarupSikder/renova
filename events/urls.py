from django.urls import path
from .views import (
    home,
    all_events,
    add_event,
    redirect_dashboard,
    dashboard_view,   # you might not need this if not used anymore
    event_detail,
    edit_event,
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
    path('all_events/', all_events, name='all_events'),

    # Redirect dashboard root to profile edit
    # path('dashboard/', redirect_dashboard, name='dashboard_redirect'),
    path('dashboard/', dashboard_view, name='dashboard'),

    # Profile edit page
    path('dashboard/profile/edit/', edit_profile, name='edit_profile'),

    # Event detail and RSVP
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),

    # Admin controls
    path('dashboard/users/', users_control_view, name='users_control'),

    # Organizer controls
    path('dashboard/events/control/', events_control_view, name='events_control'),
    path('dashboard/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('dashboard/<int:event_id>/delete/', delete_event, name='delete_event'),
    path('dashboard/categories/control/', categories_control_view, name='categories_control'),
    path('dashboard/add_event/', add_event, name='add_event'),

    # Participant controls
    path('dashboard/attended-events/', attended_events, name='attended_events'),
]