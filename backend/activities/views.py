from datetime import datetime
from uuid import UUID

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from pydantic import Field

from .models import Activity, Enrollment, Participant
from .representations import (
    serialize_activities,
    serialize_activity,
    serialize_enrollment,
)

api = NinjaAPI(title="Activities API", version="1.0.0")


class ActivityOut(Schema):
    id: UUID = Field(description="Identificador único de la actividad.")
    title: str = Field(description="Nombre visible de la actividad.")
    starts_at: datetime = Field(description="Fecha y hora de inicio en ISO 8601.")
    capacity: int = Field(ge=0, description="Cantidad máxima de participantes.")
    available_slots: int = Field(description="Cupos disponibles en este momento.")


class EnrollmentOut(Schema):
    activity_id: UUID = Field(description="Identificador de la actividad.")
    participant_id: UUID = Field(description="Identificador del participante.")
    enrolled_at: datetime = Field(description="Fecha y hora de inscripción en ISO 8601.")


def _get_demo_participant(request):
    """
    Resuelve el participante "actual" a partir de un header controlado por el
    entorno de pruebas. No es autenticación real: sólo le dice a la API para
    qué participante operar en esta petición.
    """
    participant_id = (
        request.headers.get("X-Demo-Participant-Id")
        or request.headers.get("X-Participant-Id")
        or request.headers.get("X-Demo-User-Id")
    )

    if not participant_id:
        return None

    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValidationError, ValueError):
        return None


@api.get("/activities", response=list[ActivityOut], tags=["Activities"])
def list_activities(request):
    activities = Activity.objects.order_by("starts_at")
    return serialize_activities(activities)


@api.get("/activities/{activity_id}", response=ActivityOut, tags=["Activities"])
def get_activity(request, activity_id: UUID):
    activity = get_object_or_404(Activity, id=activity_id)
    return serialize_activity(activity)


@api.get("/me/enrollments", response=list[EnrollmentOut], tags=["Enrollments"])
def list_enrollments(request):
    participant = _get_demo_participant(request)
    if participant is None:
        raise HttpError(
            400,
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)",
        )

    enrollments = (
        Enrollment.objects
        .filter(participant=participant)
        .select_related("activity")
        .order_by("enrolled_at")
    )
    return [serialize_enrollment(e) for e in enrollments]


@api.put(
    "/me/enrollments/{activity_id}",
    response={200: EnrollmentOut, 201: EnrollmentOut},
    tags=["Enrollments"],
)
def enroll(request, activity_id: UUID):
    participant = _get_demo_participant(request)
    if participant is None:
        raise HttpError(
            400,
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)",
        )

    activity = get_object_or_404(Activity, id=activity_id)

    enrollment = Enrollment.objects.filter(
        participant=participant, activity=activity
    ).first()
    if enrollment is not None:
        # Ya estaba inscripto: operación idempotente.
        return 200, serialize_enrollment(enrollment)

    current_enrollments = Enrollment.objects.filter(activity=activity).count()
    if current_enrollments >= activity.capacity:
        raise HttpError(409, "No quedan cupos disponibles para esta actividad.")

    enrollment = Enrollment.objects.create(participant=participant, activity=activity)
    return 201, serialize_enrollment(enrollment)


@api.delete("/me/enrollments/{activity_id}", response={204: None}, tags=["Enrollments"])
def unenroll(request, activity_id: UUID):
    participant = _get_demo_participant(request)
    if participant is None:
        raise HttpError(
            400,
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)",
        )

    activity = get_object_or_404(Activity, id=activity_id)
    Enrollment.objects.filter(participant=participant, activity=activity).delete()
    return 204, None


@require_GET
def activity_list(request):
    activities = Activity.objects.all()
    return render(
        request,
        "activities/activity_list.html",
        {"activities": activities},
    )