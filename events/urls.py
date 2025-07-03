from django.urls import path
from .views import home, all_events, add_event, dashboard, event_detail

urlpatterns = [
    path('home/', home, name='home'),
    path('all_events/', all_events, name='all_events'),
    path('add_event/', add_event, name='add_event'),
    path('dashboard/', dashboard, name='dashboard'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
]
