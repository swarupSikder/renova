from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
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
    profile_view,
    CustomPasswordChangeView,  # ✅ import your custom view
    CustomPasswordResetView
)

urlpatterns = [
    path('home/', home, name='home'),

    path('all_events/', AllEventsView.as_view(), name='all_events'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    path('dashboard/profile/', profile_view, name='profile'),
    path('dashboard/profile/edit/', edit_profile, name='edit_profile'),

    path('event/<int:event_id>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/rsvp/', rsvp_event, name='rsvp_event'),

    path('dashboard/users/', users_control_view, name='users_control'),
    path('dashboard/events/control/', events_control_view, name='events_control'),
    path('dashboard/add_event/', AddEventView.as_view(), name='add_event'),
    path('dashboard/<int:event_id>/edit/', EditEventView.as_view(), name='edit_event'),
    path('dashboard/<int:event_id>/delete/', delete_event, name='delete_event'),
    path('dashboard/categories/control/', categories_control_view, name='categories_control'),

    path('dashboard/attended-events/', attended_events, name='attended_events'),
    path('dashboard/redirect/', redirect_dashboard, name='dashboard_redirect'),


    # Change Password (custom view)
    path(
        'dashboard/change-password/',
        CustomPasswordChangeView.as_view(),
        name='change_password'
    ),
    path(
        'dashboard/change-password/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='events/change_password_done.html'
        ),
        name='password_change_done'
    ),

    # Reset Password (custom view)
    path(
        'dashboard/reset-password/',
        CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'dashboard/reset-password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='events/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'dashboard/reset-password/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='events/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'dashboard/reset-password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='events/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]