from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/        -> List all tasks (supports ?is_completed=true/false&priority=high)
    POST /api/tasks/        -> Create a new task
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority']

    def get_queryset(self):
        queryset = Task.objects.all()
        is_completed = self.request.query_params.get('is_completed')
        priority = self.request.query_params.get('priority')

        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/<id>/  -> Retrieve a single task
    PUT    /api/tasks/<id>/  -> Update a task (full update)
    PATCH  /api/tasks/<id>/  -> Partially update a task
    DELETE /api/tasks/<id>/  -> Delete a task
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskCompleteView(APIView):
    """
    PATCH /api/tasks/<id>/complete/  -> Toggle task completion status
    """
    def patch(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        task.is_completed = not task.is_completed
        task.save()
        serializer = TaskSerializer(task)
        return Response({
            'message': f"Task marked as {'completed' if task.is_completed else 'incomplete'}.",
            'task': serializer.data
        }, status=status.HTTP_200_OK)


class TaskStatsView(APIView):
    """
    GET /api/tasks/stats/  -> Get task statistics
    """
    def get(self, request):
        total = Task.objects.count()
        completed = Task.objects.filter(is_completed=True).count()
        pending = total - completed
        return Response({
            'total_tasks': total,
            'completed': completed,
            'pending': pending,
            'completion_rate': f"{(completed / total * 100):.1f}%" if total > 0 else "0%"
        }, status=status.HTTP_200_OK)

