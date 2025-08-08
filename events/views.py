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


def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            if u.groups.filter(name__in=group_names).exists():
                return True
        return False
    return user_passes_test(in_groups)


def index(request):
    return render(request, "events/home.html")


def home(request):
    return render(request, "events/home.html")


def all_events(request):
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
    event = get_object_or_404(Event, pk=event_id)
    return render(request, "events/event_detail.html", {"event": event})


@login_required
@group_required('Organizer', 'Admin')  # Only Organizer and Admin can add events
def add_event(request):
    if request.method == "POST":
        form = EventModelForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Make sure Event model has created_by field!
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('all_events')
    else:
        form = EventModelForm()

    return render(request, "events/add_event.html", {"form": form})


@login_required
@group_required('Organizer', 'Admin')
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.user.groups.filter(name='Organizer').exists() and event.created_by != request.user:
        messages.error(request, "You are not allowed to edit this event.")
        return redirect('dashboard')

    if request.method == "POST":
        form = EventModelForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('all_events')
    else:
        form = EventModelForm(instance=event)

    return render(request, "events/edit_event.html", {
        "form": form,
        "event": event
    })


@login_required
@group_required('Organizer', 'Admin')
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Permission check
    if request.user.groups.filter(name='Organizer').exists() and event.created_by != request.user:
        messages.error(request, "You are not allowed to delete this event.")
        return redirect('dashboard')

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('dashboard')

    return render(request, "events/delete_confirm.html", {"event": event})


@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    user = request.user

    if event.rsvps.filter(id=user.id).exists():
        messages.warning(request, "You have already RSVP'd to this event.")
    else:
        event.rsvps.add(user)
        messages.success(request, "You successfully RSVP'd to the event.")

        # Send confirmation email
        send_mail(
            subject=f"RSVP Confirmation for {event.name}",
            message=f"Hello {user.first_name},\n\nYou have successfully RSVP'd for the event '{event.name}' on {event.date}.\n\nThank you!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )
    return redirect('event_detail', event_id=event.id)


@login_required
@group_required('Admin')
def admin_dashboard(request):
    # Redirect to users_control by default
    return redirect('users_control')


@login_required
@group_required('Organizer')
def organizer_dashboard(request):
    organizer_events = Event.objects.filter(created_by=request.user).select_related('category').order_by('-date')
    categories = Category.objects.all()

    context = {
        'events': organizer_events,
        'categories': categories,
    }
    return render(request, 'events/organizer_dashboard.html', context)


@login_required
@group_required('Participant')
def participant_dashboard(request):
    user = request.user
    rsvp_events = user.rsvp_events.all().order_by('-date')

    context = {
        'rsvp_events': rsvp_events,
    }
    return render(request, 'events/participant_dashboard.html', context)


@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return redirect('admin_dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer_dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant_dashboard')
    else:
        messages.error(request, "You don't have access to any dashboards.")
        return redirect('home')
    


@login_required
@group_required('Admin')
def users_control_view(request):
    users = User.objects.all().order_by('username')
    groups = ['Participant', 'Organizer', 'Admin']  # Allowed groups

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, pk=user_id)

        if action == 'delete':
            # Prevent deleting superuser accidentally
            if user.is_superuser:
                messages.error(request, "Cannot delete superuser.")
            else:
                user.delete()
                messages.success(request, f'User {user.username} deleted successfully.')

        elif action == 'toggle_active':
            # Update user is_active to checkbox value (sent only if checked)
            # Because checkbox sends no value if unchecked, just toggle in backend:
            # We'll just flip it since we don't get actual is_active from form.
            user.is_active = not user.is_active
            user.save()
            messages.success(request, f'User {user.username} active status updated.')

        elif action == 'change_role':
            new_role = request.POST.get('new_role')

            # If no role selected, do nothing
            if new_role not in groups:
                messages.error(request, "Invalid role selected.")
            else:
                # Clear existing groups except for superusers
                if not user.is_superuser:
                    user.groups.clear()

                    # Assign new group
                    group = Group.objects.get(name=new_role)
                    user.groups.add(group)

                    messages.success(request, f"User {user.username}'s role changed to {new_role}.")

        return redirect('users_control')

    return render(request, 'events/users_control.html', {'users': users, 'groups': groups})




@login_required
@group_required('Admin')
def events_control_view(request):
    events = Event.objects.all().order_by('-date')

    if request.method == "POST":
        event_id = request.POST.get('event_id')
        action = request.POST.get('action')
        event = get_object_or_404(Event, pk=event_id)
        if action == 'delete':
            event.delete()
            messages.success(request, f'Event "{event.name}" deleted successfully.')
            return redirect('events_control')

    return render(request, 'events/events_control.html', {'events': events})


@login_required
@group_required('Admin')
def categories_control_view(request):
    categories = Category.objects.all()

    if request.method == "POST":
        action = request.POST.get('action')
        if action == "add":
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                Category.objects.create(name=name, description=description)
                messages.success(request, f'Category "{name}" added successfully.')
            else:
                messages.error(request, "Category name is required.")
        elif action == "delete":
            cat_id = request.POST.get('category_id')
            category = get_object_or_404(Category, pk=cat_id)
            category.delete()
            messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('categories_control')

    return render(request, 'events/categories_control.html', {'categories': categories})