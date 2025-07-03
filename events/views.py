from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import EventModelForm
from django.contrib import messages
from .models import Event, Participant
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
    search_query = request.GET.get('q', '')  # get ?q=searchText or empty string
    if search_query:
        events = Event.objects.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    else:
        events = Event.objects.all()
    
    return render(request, "events/all_events.html", {
        "events": events,
        "query": search_query,
    })







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