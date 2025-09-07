from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max
from .models import Project, Task, ProjectMembership
from .serializers import ProjectSerializer, TaskSerializer, ProjectMembershipSerializer

class IsProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Project):
            return ProjectMembership.objects.filter(project=obj, user=request.user).exists()
        if isinstance(obj, Task):
            return ProjectMembership.objects.filter(project=obj.project, user=request.user).exists()
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsProjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj if isinstance(obj, Project) else obj.project
        return ProjectMembership.objects.filter(project=project, user=request.user, role=ProjectMembership.Role.OWNER).exists()

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(memberships__user=self.request.user).distinct()

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ProjectMembership.objects.get_or_create(project=project, user=self.request.user, role=ProjectMembership.Role.OWNER)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsProjectOwner()]
        return [permissions.IsAuthenticated(), IsProjectMember()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsProjectOwner])
    def add_member(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectMembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = serializer.save(project=project)
        return Response(ProjectMembershipSerializer(membership).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsProjectOwner])
    def remove_member(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        ProjectMembership.objects.filter(project=project, user_id=user_id).exclude(user_id=project.owner_id).delete()
        return Response({'status': 'removed'})

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filterset_fields = ['project', 'status', 'priority', 'assignee']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'updated_at', 'order']

    def get_queryset(self):
        return Task.objects.filter(project__memberships__user=self.request.user).distinct()

    def get_permissions(self):
        return [permissions.IsAuthenticated(), IsProjectMember()]

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        task = self.get_object()
        status = request.data.get('status')
        if status and status in Task.Status.values:
            task.status = status
            max_order = Task.objects.filter(project=task.project, status=status).aggregate(Max('order'))['order__max'] or 0
            task.order = max_order + 1
            task.save(update_fields=['status', 'order', 'updated_at'])
        return Response(TaskSerializer(task).data)
