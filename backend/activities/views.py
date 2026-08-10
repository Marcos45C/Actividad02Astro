from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Activity


@require_GET
def activity_list(request):
    activities = Activity.objects.all()
    return render(
        request,
        "activities/activity_list.html",
        {"activities": activities},
    )
