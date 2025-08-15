from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeStampedModel(models.Model):
    #created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Task(TimeStampedModel, models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    duration_in_hours = models.PositiveIntegerField(default=1, help_text="Duration from creation (in hours)")
    due_at = models.DateTimeField()
    start_at = models.DateTimeField(help_text="When this task should start", default=timezone.now)

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    prompted = models.BooleanField(default=False)  # check whether the user has been prompted after due date


    def __str__(self):
        return self.title

    @property
    def dynamic_status(self):
        now = timezone.now()

        if self.is_completed:
            return 'completed'
        if now > self.due_at:
            return 'overdue'
        if self.start_at <= now <= self.due_at:
            return 'in_progress'
        if now < self.start_at:
            return 'pending'
        return 'pending'  # fallback