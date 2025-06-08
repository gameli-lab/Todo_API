from django.shortcuts import render
from rest_framework import status,  generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer, TaskSerializer, TaskStatusSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .models import Task
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters
from .models import Task
from django.utils import timezone


class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "User registered successfully",
                        "data": serializer.data
                        },
                        status = status.HTTP_201_CREATED
                        )
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors
                    },
                    status = status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "An error occurred during registration",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class MyView(APIView):
    permission_class = [IsAuthenticated]

    def get(self, request):
        pass 

class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    status_changed_after = django_filters.DateTimeFilter(field_name='status_changed_at', lookup_expr='gte')
    
    class Meta:
        model = Task
        fields = ['status', 'title', 'description', 'due_date', 'due_date_before', 
                  'due_date_after', 'status_changed_after']

class TaskList(generics.ListCreateAPIView):
    #queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'due_date', 'title', 'description', 'status_changed_at']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'status_changed_at']
 

    def get_queryset(self):
        """Return tasks filtered by the current user."""
        queryset = Task.objects.filter(user=self.request.user)
        due_date_after = self.request.query_params.get('due_date_after')
        due_date_before = self.request.query_params.get('due_date_before')
        is_overdue = self.request.query_params.get('is_overdue')
        
        if due_date_after:
            queryset = queryset.filter(due_date__gte=due_date_after)
        if due_date_before:
            queryset = queryset.filter(due_date__lte=due_date_before)
        if is_overdue and is_overdue.lower() == 'true':
            queryset = queryset.filter(due_date__lt=timezone.now(), status__in=['pending', 'in_progress'])
            
        return queryset
    
    def perform_create(self, serializer):
        """Assign current user when creating a task."""
        return serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """creating the task."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to create task.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        """List tasks related to a user."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    "success": True,
                    "message": "Tasks retrieved successfully.",
                    "data": serializer.data
                })
                
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                "success": True,
                "message": "Tasks retrieved successfully.",
                "data": serializer.data
            })
        except Exception as e:
            return Response({
                "success": False,
                "message": "Failed to retrieve tasks.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    #queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only show tasks belonging to this user."""
        return Task.objects.filter(user=self.request.user)
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'success': True,
            'message': "Tasks retrieved successfully.",
            'data': data['data'] if 'data' in data else data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve tasks belonging to this user"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "success": True,
                    "message": "Tasks retrieved successfully.",
                    "data": serializer.data
                },
                status = status.HTTP_200_OK
            )
        except Http404:
            return Response(
                {
                    "success": False,
                    "message": "Task not found",
                    "detail": "The requested task could not be found"
                },
                status = status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to retrieve tasks.",
                    "error": str(e)
                },
                status = status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Updates tasks for a user."""
        try:
            response = super().update(request, *args, **kwargs)
            return Response(
                {
                    "success": True,
                    "message": "Task updated successfully",
                    "data": response.data
                },
                status = status.HTTP_200_OK
            )
        except Http404:
            return Response(
                {
                    "success": False,
                    "message": "Task not found.",
                    "detail": "The requested task could not be found"
                },
                status = status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to update task.",
                    "error": str(e)
                },
                status = status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def destroy(self, request, *args, **kwargs):
        """Delete a task"""
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "success": True,
                    "message": "Task deleted successfully."
                },
                status = status.HTTP_204_NO_CONTENT
            )
        except Http404:
            return Response(
                {
                    "success": False,
                    "message": "Task not found",
                    "detail": "The requested task could not be found"
                },
                status = status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Failed to delete task.",
                    "error": str(e)
                },
                status = status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_status(request, pk):
    """update only the status field of a task"""
    try:
        task = get_object_or_404(Task, pk=pk, user=request.user)
        serializer = TaskStatusSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Task status updated successfully.",
                    "data": {
                        "id": task.id,
                        "status": serializer.data['status']
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success": False,
                    "message": "Validation error",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except Http404:
        return Response(
            {
                "success": False,
                "message": "Task not found",
                "detail": "The requested task could not be found"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {
                "success": False,
                "message": "Failed to update task status.",
                "error": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )