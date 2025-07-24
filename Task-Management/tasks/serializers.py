from datetime import timedelta
from venv import logger

from django.utils import timezone
from .models import Task
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.timezone import localtime
import logging

class TaskSerializer(serializers.ModelSerializer):
    is_completed = serializers.BooleanField(required=False)
    prompted = serializers.BooleanField(required=False)
    status = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    duration_in_hours = serializers.IntegerField(min_value=1)
    due_at = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    # Accept both ISO and DD-MM-YYYY HH:MM:SS formats
    start_at = serializers.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M:%S"]
    )


    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description',
            'priority', 'duration_in_hours', 'start_at', 'due_at',
            'status', 'is_completed', 'completed_at', 'prompted',
            'created_at', 'updated_at',
        ]
        read_only_fields = (
            'id', 'user', 'status', 'created_at', 'updated_at', 'due_at'
        )
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': True},
            'priority': {'required': True},
            'duration_in_hours': {'required': True},
        }

    def format_datetime(self, dt):
        return localtime(dt).strftime('%Y-%m-%d %H:%M:%S') if dt else None

    def get_completed_at(self, obj):
        return self.format_datetime(obj.completed_at) if obj.completed_at else "Not completed"

    def get_start_at(self, obj):
        return self.format_datetime(obj.start_at)

    def get_due_at(self, obj):
        return self.format_datetime(obj.due_at)

    def get_created_at(self, obj):
        return self.format_datetime(obj.created_at)

    def get_updated_at(self, obj):
        return self.format_datetime(obj.updated_at)

    def get_status(self, obj):
        return obj.dynamic_status

    def validate_is_completed(self, value):
        return value if value is not None else False

    def validate_start_at(self, value):
        if timezone.is_naive(value):
            value = timezone.make_aware(value)

        if value < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        start_at = validated_data.get('start_at')
        duration = validated_data.get('duration_in_hours')

        if not start_at or duration is None:
            raise serializers.ValidationError("Both start_at and duration_in_hours are required.")

        if not isinstance(duration, int) or duration <= 0:
            raise serializers.ValidationError({
                'duration_in_hours': "Duration must be a positive integer."
            })

        validated_data['due_at'] = start_at + timedelta(hours=duration)
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):

        request = self.context.get('request')
        user = request.user if request else None

        # Only the owner of the task can update it
        if instance.user != user:
            raise serializers.ValidationError("You do not have permission to modify this task!")

        #logger = logging.getLogger(__name__)
        #logger.warning(f'validated_data: {validated_data}')

        is_completed = validated_data.get('is_completed')
        #logger.warning(f"is_completed from request: {is_completed}")
        #logger.warning(f"Instance.is_completed before update: {instance.is_completed}")

        if is_completed is False and instance.is_completed:
                raise serializers.ValidationError({
                    'is_completed': 'A completed task cannot be marked as incomplete.'
    })

        if is_completed is True and not instance.is_completed:
            validated_data['completed_at'] = timezone.now()

        # Prevent marking completed task as incomplete
        """if not is_completed and instance.is_completed:
            raise serializers.ValidationError({
                'is_completed': 'An already completed task cannot be marked as incomplete.'
            })"""

        # Only recalculate due_at if start_at or duration changes
        start_at = validated_data.get('start_at', instance.start_at)
        duration = validated_data.get('duration_in_hours', instance.duration_in_hours)

        if 'start_at' in validated_data or 'duration_in_hours' in validated_data:
            validated_data['due_at'] = start_at + timedelta(hours=duration)

        return super().update(instance, validated_data)

