# Create your tests here.
# tests/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

class TaskCompletionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='olajide', password='testpass123')
        self.client = APIClient()

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        # Authenticate user with JWT
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test Description',
            priority='medium',
            duration_in_hours=2,
            start_at=timezone.now(),
            is_completed=False,
            due_at=timezone.now() + timedelta(days=1),
        )

    def test_mark_task_as_completed_sets_completed_at(self):
        url = f'/api/tasks/{self.task.id}'
        response = self.client.patch(url, {'is_completed': True}, format='json')

        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()

        self.assertTrue(self.task.is_completed)
        self.assertIsNotNone(self.task.completed_at)
        self.assertLessEqual(self.task.completed_at, timezone.now())

    def test_cannot_uncomplete_a_completed_task(self):
        # First, mark as completed
        self.task.is_completed = True
        self.task.completed_at = timezone.now()
        self.task.save()

        # Then, try to revert it
        url = f'/api/tasks/{self.task.id}'
        response = self.client.patch(url, {'is_completed': False}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('A completed task cannot be marked as incomplete.', str(response.data))


