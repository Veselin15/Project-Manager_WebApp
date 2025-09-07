from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Project, ProjectMembership, Task

class _BaseProjectAccessMixin(UserPassesTestMixin):
    def resolve_project(self):
        # 1) If view already has an object, derive project from it
        obj = getattr(self, 'object', None)
        if obj is not None:
            if hasattr(obj, 'project') and obj.project:
                return obj.project
            if isinstance(obj, Project):
                return obj
        # 2) Explicit project_pk in URL
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            return get_object_or_404(Project, pk=project_pk)
        # 3) pk may refer to Task or Project
        pk = self.kwargs.get('pk')
        if pk is not None:
            try:
                task = Task.objects.select_related('project').get(pk=pk)
                return task.project
            except Task.DoesNotExist:
                return get_object_or_404(Project, pk=pk)
        return None

class OwnerRequiredMixin(_BaseProjectAccessMixin):
    def test_func(self):
        project = self.resolve_project()
        return project is not None and ProjectMembership.objects.filter(
            project=project, user=self.request.user, role=ProjectMembership.Role.OWNER
        ).exists()

class MemberRequiredMixin(_BaseProjectAccessMixin):
    def test_func(self):
        project = self.resolve_project()
        return project is not None and ProjectMembership.objects.filter(
            project=project, user=self.request.user
        ).exists()
