import json
from datetime import datetime
from uuid import UUID

from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from ninja import NinjaAPI, Schema
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
    starts_at: datetime = Field(description="Fecha en ISO 8601.")
    capacity: int = Field(
        ge=0,
        description="Cantidad máxima de participantes.",
        examples=[30],
    )


class EnrollmentOut(Schema):
    activity_id: UUID = Field(description="Identificador de la actividad.")
    participant_id: UUID = Field(description="Identificador del participante.")
    enrolled_at: datetime = Field(description="Fecha y hora de inscripción en ISO 8601.")


@api.get(
    "/activities",
    response=list[ActivityOut],
    tags=["Activities"],
)
def ninja_list_activities(request):
    activities = Activity.objects.order_by("starts_at")
    return [
        {
            "id": a.id,
            "title": a.title,
            "starts_at": timezone.localtime(a.starts_at),
            "capacity": a.capacity,
        }
        for a in activities
    ]


@api.get(
    "/activities/{activity_id}",
    response=ActivityOut,
    tags=["Activities"],
)
def ninja_get_activity(request, activity_id: UUID):
    activity = get_object_or_404(Activity, id=activity_id)
    return {
        "id": activity.id,
        "title": activity.title,
        "starts_at": timezone.localtime(activity.starts_at),
        "capacity": activity.capacity,
    }


@api.get(
    "/me/enrollments",
    response=list[EnrollmentOut],
    tags=["Enrollments"],
)
def ninja_list_enrollments(request):
    participant = _get_demo_participant(request)
    if participant is None:
        return HttpResponseBadRequest(
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)"
        )
    enrollments = (
        Enrollment.objects
        .filter(participant=participant)
        .select_related("activity")
        .order_by("enrolled_at")
    )
    return [
        {
            "activity_id": e.activity_id,
            "participant_id": e.participant_id,
            "enrolled_at": timezone.localtime(e.enrolled_at),
        }
        for e in enrollments
    ]


@api.put(
    "/me/enrollments/{activity_id}",
    response={201: EnrollmentOut, 200: EnrollmentOut},
    tags=["Enrollments"],
)
def ninja_enroll(request, activity_id: UUID):
    participant = _get_demo_participant(request)
    if participant is None:
        return HttpResponseBadRequest(
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)"
        )

    activity = get_object_or_404(Activity, id=activity_id)

    enrollment = Enrollment.objects.filter(
        participant=participant, activity=activity
    ).first()
    if enrollment is not None:
        return 200, {
            "activity_id": enrollment.activity_id,
            "participant_id": enrollment.participant_id,
            "enrolled_at": timezone.localtime(enrollment.enrolled_at),
        }

    current_enrollments = Enrollment.objects.filter(activity=activity).count()
    if current_enrollments >= activity.capacity:
        return HttpResponse(
            json.dumps({"detail": "No quedan cupos disponibles para esta actividad."}),
            status=409,
            content_type="application/json",
        )

    enrollment = Enrollment.objects.create(participant=participant, activity=activity)
    return 201, {
        "activity_id": enrollment.activity_id,
        "participant_id": enrollment.participant_id,
        "enrolled_at": timezone.localtime(enrollment.enrolled_at),
    }


@api.delete(
    "/me/enrollments/{activity_id}",
    response={204: None},
    tags=["Enrollments"],
)
def ninja_unenroll(request, activity_id: UUID):
    participant = _get_demo_participant(request)
    if participant is None:
        return HttpResponseBadRequest(
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)"
        )

    activity = get_object_or_404(Activity, id=activity_id)
    Enrollment.objects.filter(participant=participant, activity=activity).delete()
    return 204, None


def _get_demo_participant(request):
    """
    Resuelve el participante "actual" a partir de un header controlado por el
    entorno de pruebas. No es autenticación real: sólo le dice a la API para
    qué participante operar en esta actividad.
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
    return JsonResponse(payload, safe=False)


@require_GET
def activity_api_detail(request, id):
    activity = get_object_or_404(Activity, id=id)
    return JsonResponse(serialize_activity(activity))


@require_GET
def activity_api_enrollments(request):
    participant = _get_demo_participant(request)
    if participant is None:
        return HttpResponseBadRequest(
            "Falta o no se reconoce la identidad de demostración "
            "(header X-Demo-Participant-Id)"
        )

    enrollments = (
        Enrollment.objects
        .filter(participant=participant)
        .select_related("activity")
        .order_by("enrolled_at")
    )
    payload = [serialize_enrollment(e) for e in enrollments]
    return JsonResponse(payload, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class EnrollmentDetailView(View):
    """
    Maneja /api/v1/me/enrollments/{activity_id}/
    Cada verbo HTTP tiene su propio método. Cualquier otro verbo
    (GET, POST, etc.) devuelve 405 automáticamente.
    """

    def put(self, request, activity_id):
        participant = _get_demo_participant(request)
        if participant is None:
            return HttpResponseBadRequest(
                "Falta o no se reconoce la identidad de demostración "
                "(header X-Demo-Participant-Id)"
            )

        activity = get_object_or_404(Activity, id=activity_id)

        enrollment = Enrollment.objects.filter(
            participant=participant, activity=activity
        ).first()
        if enrollment is not None:
            # Ya estaba inscripto: operación idempotente.
            return JsonResponse(serialize_enrollment(enrollment), status=200)

        current_enrollments = Enrollment.objects.filter(activity=activity).count()
        if current_enrollments >= activity.capacity:
            return JsonResponse(
                {"detail": "No quedan cupos disponibles para esta actividad."},
                status=409,
            )

        enrollment = Enrollment.objects.create(participant=participant, activity=activity)
        return JsonResponse(serialize_enrollment(enrollment), status=201)

    def delete(self, request, activity_id):
        participant = _get_demo_participant(request)
        if participant is None:
            return HttpResponseBadRequest(
                "Falta o no se reconoce la identidad de demostración "
                "(header X-Demo-Participant-Id)"
            )

        activity = get_object_or_404(Activity, id=activity_id)
        Enrollment.objects.filter(participant=participant, activity=activity).delete()
        return HttpResponse(status=204)


@require_http_methods(["PUT"])
@csrf_exempt  # Desactivar la verificación CSRF para esta vista
def activity_put(request, id):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON inválido")

    activity = get_object_or_404(Activity, id=id)

    title = body.get("title")
    starts_at = body.get("starts_at")
    capacity = body.get("capacity")

    if title is not None:
        activity.title = title

    if starts_at is not None:
        dt = parse_datetime(starts_at)
        if dt is None:
            return HttpResponseBadRequest("Formato de fecha inválido para 'starts_at'")
        activity.starts_at = dt

    if capacity is not None:
        try:
            capacity_val = int(capacity)
            if capacity_val < 0:
                raise ValueError()
        except ValueError:
            return HttpResponseBadRequest("'capacity' debe ser un entero no negativo")
        activity.capacity = capacity_val

    activity.save()

    return JsonResponse({"data": serialize_activity(activity)})