import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .models import Activity, Enrollment, Participant
from .representations import (
    serialize_activities,
    serialize_activity,
    serialize_enrollment,
)


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
    return JsonResponse({"data": payload})


@require_GET
def activity_api_detail(request, id):
    activity = get_object_or_404(Activity, id=id)
    return JsonResponse({"data": serialize_activity(activity)})


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