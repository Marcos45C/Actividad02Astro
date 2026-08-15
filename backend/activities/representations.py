from django.utils import timezone

from .models import Enrollment


def serialize_activity(activity):
    available_slots = activity.capacity - Enrollment.objects.filter(activity=activity).count()

    return {
        "id": activity.id,
        "title": activity.title,
        "starts_at": timezone.localtime(activity.starts_at).isoformat(),
        "capacity": activity.capacity,
        "available_slots": available_slots,
    }


def serialize_activities(activities):
    return [serialize_activity(activity) for activity in activities]


def serialize_enrollment(enrollment):
    return {
        "activity_id": str(enrollment.activity_id),
        "participant_id": str(enrollment.participant_id),
        "enrolled_at": timezone.localtime(enrollment.enrolled_at).isoformat(),
    }