from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .forms import EventModelForm
from .models import Event, Participant, Category




# Get User
User = settings.AUTH_USER_MODEL

# Try to import OrganizerProfile if it exists (optional profile model)
try:
    from .models import OrganizerProfile
except Exception:
    OrganizerProfile = None

# ----------------------------------------
# Group-based access control decorator
# ----------------------------------------
def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            if u.groups.filter(name__in=group_names).exists():
                return True
        return False
    return user_passes_test(in_groups)

# ----------------------------------------
# GroupRequiredMixin for CBVs
# ----------------------------------------
class GroupRequiredMixin(UserPassesTestMixin):
    group_names = []

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        return user.groups.filter(name__in=self.group_names).exists()

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        return redirect('dashboard_redirect')

# ----------------------------------------
# CBVs for requested views
# ----------------------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "events/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()
        is_organizer = user.groups.filter(name='Organizer').exists()
        is_participant = not (is_admin or is_organizer)

        context.update({
            "user": user,
            "is_admin": is_admin,
            "is_organizer": is_organizer,
            "is_participant": is_participant,
            "can_add_event": is_admin or is_organizer,
            "show_profile_edit": True,
        })

        if is_admin:
            context["users"] = User.objects.all()
            context["total_events"] = Event.objects.count()
        elif is_organizer:
            context["events"] = Event.objects.filter(created_by=user).order_by('-date')
        else:
            context["events"] = Event.objects.filter(rsvps=user).order_by('-date')

        return context


class AllEventsView(ListView):
    model = Event
    template_name = "events/all_events.html"
    context_object_name = 'events'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category').prefetch_related('rsvps').order_by('-date')
        search_query = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        filters = Q()
        if search_query:
            filters &= Q(name__icontains=search_query) | Q(location__icontains=search_query)
        if category_id:
            filters &= Q(category__id=category_id)
        if start_date and end_date:
            filters &= Q(date__range=[start_date, end_date])

        return queryset.filter(filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.request.GET.get('q', ''),
            'categories': Category.objects.all(),
            'total_participants': Participant.objects.count(),
            'selected_category': self.request.GET.get('category'),
            'start_date': self.request.GET.get('start_date'),
            'end_date': self.request.GET.get('end_date'),
        })
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    pk_url_kwarg = 'event_id'


class AddEventView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Event
    form_class = EventModelForm
    template_name = "events/add_event.html"
    success_url = reverse_lazy('dashboard_redirect')
    group_names = ['Organizer', 'Admin']

    def form_valid(self, form):
        event = form.save(commit=False)
        event.created_by = self.request.user
        event.save()
        messages.success(self.request, "Event created successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors in the form.")
        return super().form_invalid(form)


class EditEventView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Event
    form_class = EventModelForm
    template_name = "events/edit_event.html"
    success_url = reverse_lazy('dashboard_redirect')
    pk_url_kwarg = 'event_id'
    group_names = ['Organizer', 'Admin']

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Organizer').exists():
            event = self.get_object()
            if hasattr(event, 'created_by') and event.created_by != request.user:
                messages.error(request, "You are not allowed to edit this event.")
                return redirect('dashboard_redirect')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Event updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors in the form.")
        return super().form_invalid(form)

# ----------------------------------------
# FBVs for the rest (keep same)
# ----------------------------------------

def index(request):
    return render(request, "events/home.html")


def home(request):
    return render(request, "events/home.html")


@login_required
def redirect_dashboard(request):
    return redirect('edit_profile')


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


@login_required
def attended_events(request):
    events = Event.objects.filter(rsvps=request.user).order_by('-date')

    can_add_event = (
        request.user.is_superuser or
        request.user.groups.filter(name__in=['Admin', 'Organizer']).exists()
    )

    return render(request, "events/attended_events.html", {
        "events": events,
        "can_add_event": can_add_event
    })