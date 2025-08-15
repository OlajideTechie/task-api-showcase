from django.urls import path
from .views import UserTaskListCreateView, UserTaskDetailView

urlpatterns = [
    path('tasks/', UserTaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>', UserTaskDetailView.as_view(), name='task-detail'),
]
