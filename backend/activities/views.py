from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .representations import serialize_activity, serialize_activities

from .models import Activity


@require_GET
def activity_list(request):
    activities = Activity.objects.all()
    return render(
        request,
        "activities/activity_list.html",
        {"activities": activities},
    )

@require_GET
def activity_api_list(request):
    activities = Activity.objects.all()
    payload = serialize_activities(activities)
    # payload = [serialize_activity(activity) for activity in activities]
    return JsonResponse({"data": payload})
