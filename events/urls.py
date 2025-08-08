from django.urls import path
from .views import home, all_events, add_event, redirect_dashboard, event_detail, edit_event, delete_event, admin_dashboard, rsvp_event, organizer_dashboard, participant_dashboard, users_control_view, events_control_view, categories_control_view

urlpatterns = [
    path('home/', home, name='home'),
    path('all_events/', all_events, name='all_events'),
    path('add_event/', add_event, name='add_event'),
    path('dashboard/', redirect_dashboard, name='dashboard'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', delete_event, name='delete_event'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/users/', users_control_view, name='users_control'),
    path('admin/events/', events_control_view, name='events_control'),
    path('admin/categories/', categories_control_view, name='categories_control'),
    path('organizer/dashboard/', organizer_dashboard, name='organizer_dashboard'),
    path('participant/dashboard/', participant_dashboard, name='participant_dashboard'),
    path('event/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),
]
