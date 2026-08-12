from django.utils import timezone

def serialize_activity(activity):
   
    return {
        "id": activity.id,
        "title": activity.title,
        "starts_at":  timezone.localtime(activity.starts_at).isoformat(),
        "capacity": activity.capacity,
    }

def serialize_activities(activities):
    return [serialize_activity(activity) for activity in activities]