from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import EventModelForm
from django.contrib import messages
from .models import Event, Participant, Category
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import date

# - - - - - - - - #
#    Index View   #
# - - - - - - - - #
def index(request):
    return render(request, "events/home.html")





# - - - - - - - - #
#    Home View    #
# - - - - - - - - #
def home(request):
    return render(request, "events/home.html")





# - - - - - - - - - - - #
#    All Events View    #
# - - - - - - - - - - - #
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

    # Query optimized with select_related and prefetch_related
    events = (
        Event.objects
        .filter(filters)
        .select_related('category')
        .prefetch_related('participant_set')  # reverse relation from Participant
        .order_by('-date')
    )

    # Total number of participants across all events
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







# - - - - - - - - - - - - #
#   Events Detail View    #
# - - - - - - - - - - - - #
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, "events/event_detail.html", {"event": event})








# - - - - - - - - - - - #
#    Add Event View     #
# - - - - - - - - - - - #
def add_event(request):
    if request.method == "POST":
        form = EventModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('all_events')
    else:
        form = EventModelForm()

    return render(request, "events/add_event.html", {
        "form": form
    })








# - - - - - - - - - - - #
#     Edit Event View   #
# - - - - - - - - - - - #
def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        form = EventModelForm(request.POST, request.FILES, instance=event)
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










# - - - - - - - - - - - - #
#   Delete Event View     #
# - - - - - - - - - - - - #
def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('dashboard')

    return render(request, "events/delete_confirm.html", {"event": event})










# - - - - - - - - - - - #
#     Dashboard View    #
# - - - - - - - - - - - #
def dashboard(request):
    today = date.today()
    filter_type = request.GET.get("filter", "today")  #default is today's events

    all_events = Event.objects.all()
    upcoming_events = all_events.filter(date__gt=today)
    past_events = all_events.filter(date__lt=today)
    todays_events = all_events.filter(date=today)

    # Determine which list to show
    if filter_type == "all":
        filtered_events = all_events
        filter_title = "All Events"
    elif filter_type == "upcoming":
        filtered_events = upcoming_events
        filter_title = "Upcoming Events"
    elif filter_type == "past":
        filtered_events = past_events
        filter_title = "Past Events"
    else:
        filtered_events = todays_events
        filter_title = "Today's Events"

    context = {
        "total_events": all_events.count(),
        "upcoming_events": upcoming_events.count(),
        "past_events": past_events.count(),
        "total_participants": Participant.objects.count(),
        "filtered_events": filtered_events,
        "filter_title": filter_title,
    }
    return render(request, "events/dashboard.html", context)