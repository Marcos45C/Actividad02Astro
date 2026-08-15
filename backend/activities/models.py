import uuid

from django.db import models


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=160)

    def __str__(self):
        return self.name


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)
    starts_at = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    class Meta:
        ordering = ("starts_at",)
        verbose_name_plural = "activities"

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["participant", "activity"],
                name="unique_participant_activity",
            )
        ]

    def __str__(self):
        return f"{self.participant} - {self.activity}"