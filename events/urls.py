from django.urls import path
from .views import home, all_events, add_event, dashboard, event_detail, edit_event, delete_event

urlpatterns = [
    path('home/', home, name='home'),
    path('all_events/', all_events, name='all_events'),
    path('add_event/', add_event, name='add_event'),
    path('dashboard/', dashboard, name='dashboard'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('event/<int:event_id>/edit/', edit_event, name='edit_event'),
    path('event/<int:event_id>/delete/', delete_event, name='delete_event'),
]
