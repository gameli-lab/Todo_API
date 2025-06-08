from django.urls import path
from .views import RegisterView, LoginView, TaskList, TaskDetail, update_task_status

urlpatterns = [
        path('register/', RegisterView.as_view(), name = 'register'),
        path('login/', LoginView.as_view(), name = 'login'),
        path('tasks/', TaskList.as_view(), name = 'task-list'),
        path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
        path('tasks/<int:pk>/status/', update_task_status, name='task-status'),
]
