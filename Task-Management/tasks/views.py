from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Task
from .serializers import TaskSerializer

@swagger_auto_schema(tags=["Tasks"])
class UserTaskListCreateView(generics.ListCreateAPIView):
    """
    Handles listing and creating tasks for the authenticated user.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()  # Return an empty queryset for schema generation
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Retrieve all tasks created by the authenticated user",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        custom_response_data = {
            "data": serializer.data,
            #"message": "Tasks retrieved successfully!"
        }
        return Response(custom_response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a task. The 'due_at' field is automatically calculated from 'start_at' + 'duration_in_hours'.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'description', 'priority', 'duration_in_hours', 'start_at'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, example="New Task"),
                'description': openapi.Schema(type=openapi.TYPE_STRING, example="Some task details"),
                'priority': openapi.Schema(type=openapi.TYPE_STRING, example="high"),
                'duration_in_hours': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                'start_at': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='date-time',
                    example="2025-07-13T10:00:00Z"
                ),
                'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False)
            },
        ),
        responses={201: TaskSerializer()}
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        custom_response_data = {
            "data": response.data,
            #"message": "Task created successfully!"
        }
        return Response(custom_response_data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(tags=["Tasks"])

class UserTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a task belonging to the authenticated user.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        task = super().get_object()
        if task.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this task.")
        return task

    @swagger_auto_schema(
        operation_description="Retrieve a single task by ID belonging to the authenticated user.",
        responses={
            200: TaskSerializer(),
            403: openapi.Response(description="You do not have permission to view this task."),
            404: openapi.Response(description="Task not found.")
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Fully update a task by ID belonging to the authenticated user.",
        request_body=TaskSerializer,
        responses={
            200: openapi.Response(description="Task updated successfully.", schema=TaskSerializer),
            403: openapi.Response(description="You do not have permission to update this task."),
            404: openapi.Response(description="Task not found.")
        }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update task completion status (e.g mark as completed).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_completed': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Mark task as completed or not'),
            },
            required=['is_completed'],
        ),
        responses={
            200: openapi.Response(description="Task updated successfully.", schema=TaskSerializer),
            400: openapi.Response(description="Invalid input."),
            403: openapi.Response(description="You do not have permission to update this task."),
            404: openapi.Response(description="Task not found."),
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)



    @swagger_auto_schema(
        operation_description="Delete a task by ID belonging to the authenticated user.",
        responses={
            200: openapi.Response(description="Task deleted successfully."),
            403: openapi.Response(description="You do not have permission to delete this task."),
            404: openapi.Response(description="Task not found.")
        }
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Task deleted successfully."},
            status=status.HTTP_200_OK
        )