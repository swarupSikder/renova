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
# Public Views
# ----------------------------------------
def index(request):
    return render(request, "events/home.html")


def home(request):
    return render(request, "events/home.html")


def all_events(request):
    """
    Show all events with optional filtering.
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
# Unified Dashboard View rendering profile edit by default
# ----------------------------------------
@login_required
def dashboard_view(request):
    user = request.user
    is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()
    is_organizer = user.groups.filter(name='Organizer').exists()
    is_participant = not (is_admin or is_organizer)

    context = {
        "user": user,
        "is_admin": is_admin,
        "is_organizer": is_organizer,
        "is_participant": is_participant,
        "can_add_event": is_admin or is_organizer,
    }

    # Add role-specific data
    if is_admin:
        context["users"] = User.objects.all()
        context["total_events"] = Event.objects.count()
    elif is_organizer:
        context["events"] = Event.objects.filter(created_by=user).order_by('-date')
    else:
        context["events"] = Event.objects.filter(rsvps=user).order_by('-date')

    # Pass a flag to indicate showing profile edit section by default
    context["show_profile_edit"] = True

    return render(request, "events/dashboard.html", context)






# ----------------------------------------
# Redirect to dashboard_view or profile edit
# ----------------------------------------
@login_required
def redirect_dashboard(request):
    """
    Redirect /dashboard/ to profile edit page.
    """
    # Redirect directly to profile edit page
    return redirect('edit_profile')


# ----------------------------------------
# Event CRUD
# ----------------------------------------
@login_required
@group_required('Organizer', 'Admin')
def add_event(request):
    if request.method == "POST":
        form = EventModelForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            if hasattr(event, 'created_by'):
                event.created_by = request.user
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('dashboard_redirect')  # or 'edit_profile'
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = EventModelForm()

    return render(request, "events/add_event.html", {"form": form})


@login_required
@group_required('Organizer', 'Admin')
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.user.groups.filter(name='Organizer').exists():
        if hasattr(event, 'created_by') and event.created_by != request.user:
            messages.error(request, "You are not allowed to edit this event.")
            return redirect('dashboard_redirect')

    if request.method == "POST":
        form = EventModelForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('dashboard_redirect')
        messages.error(request, "Please correct the errors in the form.")
    else:
        form = EventModelForm(instance=event)

    return render(request, "events/edit_event.html", {"form": form, "event": event})


@login_required
@group_required('Organizer', 'Admin')
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.user.groups.filter(name='Organizer').exists():
        if hasattr(event, 'created_by') and event.created_by != request.user:
            messages.error(request, "You are not allowed to delete this event.")
            return redirect('dashboard_redirect')

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('dashboard_redirect')

    return render(request, "events/delete_confirm.html", {"event": event})


# ----------------------------------------
# RSVP
# ----------------------------------------
@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if event.rsvps.filter(id=request.user.id).exists():
        messages.warning(request, "You have already attended this event.")
    else:
        event.rsvps.add(request.user)
        messages.success(request, "You have successfully attended the event.")

        try:
            send_mail(
                subject=f"Renova's Event Alert for {event.name}",
                message=(
                    f"Hello {request.user.first_name or request.user.username},\n\n"
                    f"You have successfully attended the event '{event.name}' on {event.date}.\n\nThanks!"
                ),
                from_email=getattr(settings, 'EMAIL_HOST_USER', None),
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception:
            pass

    return redirect('event_detail', event_id=event.id)


# ----------------------------------------
# Admin Control
# ----------------------------------------
@login_required
@group_required('Admin')
def users_control_view(request):
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
# Organizer/Admin Control
# ----------------------------------------
@login_required
@group_required('Organizer', 'Admin')
def events_control_view(request):
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
# Profile Edit
# ----------------------------------------
@login_required
def edit_profile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("edit_profile")

    return render(request, "events/edit_profile.html", {
        "user": request.user
    })


# ----------------------------------------
# Attended Events
# ----------------------------------------
@login_required
def attended_events(request):
    """
    Show events the current user has RSVP'd to.
    Include 'Add Event' nav permission flag.
    """
    events = Event.objects.filter(rsvps=request.user).order_by('-date')

    can_add_event = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()
    )

    return render(request, "events/attended_events.html", {
        "events": events,
        "can_add_event": can_add_event
    })