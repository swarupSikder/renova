from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.conf import settings

from .forms import EventModelForm
from .models import Event, Participant, Category

# Try to import OrganizerProfile if it exists (optional profile model)
try:
    from .models import OrganizerProfile
except Exception:
    OrganizerProfile = None


# ----------------------------------------
# Group-based access control decorator
# ----------------------------------------
def group_required(*group_names):
    """
    Decorator to restrict access to users in specific groups.
    Superusers bypass group checks.
    Usage:
      @login_required
      @group_required('Admin', 'Organizer')
      def my_view(...):
          ...
    """
    def in_groups(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            if u.groups.filter(name__in=group_names).exists():
                return True
        return False
    return user_passes_test(in_groups)


# ----------------------------------------
# Public Views (No login required)
# ----------------------------------------
def index(request):
    return render(request, "events/home.html")


def home(request):
    return render(request, "events/home.html")


def all_events(request):
    """
    Show all events with optional filtering by search query, category, and date range.
    """
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    filters = Q()
    if search_query:
        filters &= Q(name__icontains=search_query) | Q(location__icontains=search_query)
    if category_id:
        filters &= Q(category__id=category_id)
    if start_date and end_date:
        filters &= Q(date__range=[start_date, end_date])

    events = (
        Event.objects
        .filter(filters)
        .select_related('category')
        .prefetch_related('rsvps')
        .order_by('-date')
    )

    total_participants = Participant.objects.count()

    context = {
        'events': events,
        'query': search_query,
        'categories': Category.objects.all(),
        'total_participants': total_participants,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, "events/all_events.html", context)


def event_detail(request, event_id):
    """
    Show details of a single event.
    """
    event = get_object_or_404(Event, pk=event_id)
    return render(request, "events/event_detail.html", {"event": event})


# ----------------------------------------
# Dashboards & Redirects
# ----------------------------------------
@login_required
@group_required('Admin')
def admin_dashboard(request):
    """
    Admin Dashboard redirects to Users control page.
    """
    return redirect('users_control')


@login_required
@group_required('Organizer')
def organizer_dashboard(request):
    # Redirect to profile edit page by default
    return redirect('edit_profile')


@login_required
def participant_dashboard(request):
    # Redirect to profile edit page by default
    return redirect('attended_events')


@login_required
def redirect_dashboard(request):
    """
    Redirect user to their respective dashboard based on role.
    """
    user = request.user
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    else:
        return redirect('participant_dashboard')


# ----------------------------------------
# Event CRUD (Organizer/Admin)
# ----------------------------------------
@login_required
@group_required('Organizer', 'Admin')
def add_event(request):
    """
    Add new event - Organizer or Admin only.
    """
    if request.method == "POST":
        form = EventModelForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if hasattr(event, 'created_by'):
                event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('all_events')
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = EventModelForm()

    return render(request, "events/add_event.html", {"form": form})


@login_required
@group_required('Organizer', 'Admin')
def edit_event(request, event_id):
    """
    Edit existing event.
    Organizer can edit only their own events.
    """
    event = get_object_or_404(Event, pk=event_id)

    # Ownership check for Organizer
    if request.user.groups.filter(name='Organizer').exists():
        if hasattr(event, 'created_by') and event.created_by != request.user:
            messages.error(request, "You are not allowed to edit this event.")
            return redirect('dashboard')

    if request.method == "POST":
        form = EventModelForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('all_events')
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = EventModelForm(instance=event)

    return render(request, "events/edit_event.html", {"form": form, "event": event})


@login_required
@group_required('Organizer', 'Admin')
def delete_event(request, event_id):
    """
    Delete event after confirmation.
    Organizer can delete only their own events.
    """
    event = get_object_or_404(Event, pk=event_id)

    # Ownership check for Organizer
    if request.user.groups.filter(name='Organizer').exists():
        if hasattr(event, 'created_by') and event.created_by != request.user:
            messages.error(request, "You are not allowed to delete this event.")
            return redirect('dashboard')

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('dashboard')

    return render(request, "events/delete_confirm.html", {"event": event})


# ----------------------------------------
# RSVP functionality
# ----------------------------------------
@login_required
def rsvp_event(request, event_id):
    """
    RSVP current user to event.
    Sends confirmation email silently.
    """
    event = get_object_or_404(Event, pk=event_id)

    if event.rsvps.filter(id=request.user.id).exists():
        messages.warning(request, "You have already attended to this event.")
    else:
        event.rsvps.add(request.user)
        messages.success(request, "You have successfully attended to the event.")

        # Send confirmation email
        try:
            send_mail(
                subject=f"Renova's Event Alert for {event.name}",
                message=(
                    f"Hello {request.user.first_name or request.user.username},\n\n"
                    f"You have successfully attended for the event '{event.name}' on {event.date}.\n\nThanks!"
                ),
                from_email=getattr(settings, 'EMAIL_HOST_USER', None),
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception:
            # Ignore email errors
            pass

    return redirect('event_detail', event_id=event.id)


# ----------------------------------------
# Admin Control Views (User Management)
# ----------------------------------------
@login_required
@group_required('Admin')
def users_control_view(request):
    """
    Admin view to manage users: delete, activate/deactivate, change roles.
    """
    users = User.objects.all().order_by('username')
    groups = ['Participant', 'Organizer', 'Admin']

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, pk=user_id)

        if action == 'delete':
            if user.is_superuser:
                messages.error(request, "Cannot delete superuser.")
            else:
                user.delete()
                messages.success(request, f"User {user.username} deleted.")

        elif action == 'toggle_active':
            user.is_active = not user.is_active
            user.save()
            messages.success(request, f"User {user.username} active status changed.")

        elif action == 'change_role':
            new_role = request.POST.get('new_role')
            if new_role in groups and not user.is_superuser:
                user.groups.clear()
                group_obj, _ = Group.objects.get_or_create(name=new_role)
                user.groups.add(group_obj)
                messages.success(request, f"User {user.username}'s role changed to {new_role}.")
            else:
                messages.error(request, "Invalid role selected.")

        return redirect('users_control')

    return render(request, 'events/users_control.html', {'users': users, 'groups': groups})


# ----------------------------------------
# Organizer Control Views (Events & Categories)
# ----------------------------------------
@login_required
@group_required('Organizer', 'Admin')
def events_control_view(request):
    """
    Organizer/Admin view to manage all events.
    """
    events = Event.objects.all().order_by('-date')

    if request.method == "POST":
        event_id = request.POST.get('event_id')
        action = request.POST.get('action')
        event = get_object_or_404(Event, pk=event_id)
        if action == 'delete':
            event.delete()
            messages.success(request, f'Event "{event.name}" deleted.')
            return redirect('events_control')

    return render(request, 'events/events_control.html', {'events': events})


@login_required
@group_required('Organizer', 'Admin')
def categories_control_view(request):
    """
    Organizer/Admin view to add/delete categories.
    """
    categories = Category.objects.all()

    if request.method == "POST":
        action = request.POST.get('action')
        if action == "add":
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                Category.objects.create(name=name, description=description)
                messages.success(request, f'Category "{name}" added.')
            else:
                messages.error(request, "Category name is required.")
        elif action == "delete":
            cat_id = request.POST.get('category_id')
            category = get_object_or_404(Category, pk=cat_id)
            category.delete()
            messages.success(request, f'Category "{category.name}" deleted.')
        return redirect('categories_control')

    return render(request, 'events/categories_control.html', {'categories': categories})


# ----------------------------------------
# Profile Edit View
# ----------------------------------------
@login_required
def edit_profile(request):
    """
    Allow to update only first and last name.
    Preloads current data into the form.
    """
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("edit_profile")  # Stay on the same page after save

    # GET request → show current values
    return render(request, "events/edit_profile.html", {
        "user": request.user
    })








@login_required
def attended_events(request):
    # Assuming rsvps is a ManyToMany to User or a related name from another model
    events = Event.objects.filter(rsvps=request.user)
    return render(request, "events/attended_events.html", {"events": events})
