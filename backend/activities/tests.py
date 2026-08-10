from datetime import datetime
from uuid import UUID

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Activity


class ActivityListTests(TestCase):
    def test_lists_every_activity_field(self):
        activity = Activity.objects.create(
            id=UUID("1b470ddf-3e84-4b77-9aae-091d21e52bd6"),
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=30,
        )

        response = self.client.get(reverse("activities:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(activity.id))
        self.assertContains(response, activity.title)
        self.assertContains(response, "2026-03-23T18:00:00-03:00")
        self.assertContains(response, "30")

    def test_rejects_non_get_requests(self):
        response = self.client.post(reverse("activities:list"))

        self.assertEqual(response.status_code, 405)
