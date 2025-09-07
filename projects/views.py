from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from .forms import ProjectForm, TaskForm, AddCollaboratorForm
from .models import Project, Task, ProjectMembership
from .permissions import OwnerRequiredMixin, MemberRequiredMixin

User = get_user_model()

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        return response

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.filter(memberships__user=user).distinct()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

    def dispatch(self, request, *args, **kwargs):
        project = self.get_object()
        if not ProjectMembership.objects.filter(project=project, user=request.user).exists():
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        ProjectMembership.objects.get_or_create(project=self.object, user=self.request.user, role=ProjectMembership.Role.OWNER)
        return response

class ProjectUpdateView(OwnerRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

class ProjectDeleteView(OwnerRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')

class ProjectMembersView(OwnerRequiredMixin, SingleObjectMixin, FormView):
    model = Project
    form_class = AddCollaboratorForm
    template_name = 'projects/project_members.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['object'] = getattr(self, 'object', self.get_object())
        return ctx

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        self.object = self.get_object()
        username = form.cleaned_data['username']
        role = form.cleaned_data['role']
        user = User.objects.get(username=username)
        if user == self.request.user and role != ProjectMembership.Role.OWNER:
            ProjectMembership.objects.update_or_create(project=self.object, user=user, defaults={'role': ProjectMembership.Role.OWNER})
        else:
            ProjectMembership.objects.update_or_create(project=self.object, user=user, defaults={'role': role})
        messages.success(self.request, f'Added/updated collaborator {user.username}.')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if 'remove_user' in request.POST:
            self.object = self.get_object()
            uid = request.POST.get('remove_user')
            if str(self.object.owner_id) == uid:
                messages.error(request, 'Cannot remove the owner from the project.')
            else:
                ProjectMembership.objects.filter(project=self.object, user_id=uid).delete()
                messages.success(request, 'Collaborator removed.')
            return redirect(self.object.get_absolute_url())
        return super().post(request, *args, **kwargs)

# Tasks
class TaskCreateView(MemberRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        if not ProjectMembership.objects.filter(project=self.project, user=request.user).exists():
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project
        return super().form_valid(form)

    def get_success_url(self):
        return self.project.get_absolute_url()

class TaskDetailView(MemberRequiredMixin, DetailView):
    model = Task
    template_name = 'projects/task_detail.html'

class TaskUpdateView(MemberRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'projects/task_form.html'

    def get_success_url(self):
        return self.object.project.get_absolute_url()

class TaskDeleteView(MemberRequiredMixin, DeleteView):
    model = Task
    template_name = 'projects/task_confirm_delete.html'

    def get_success_url(self):
        return self.object.project.get_absolute_url()

class BoardView(MemberRequiredMixin, TemplateView):
    template_name = 'projects/board.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=kwargs['pk'])
        ctx['project'] = project
        columns = [
            (Task.Status.TODO, 'To Do'),
            (Task.Status.IN_PROGRESS, 'In Progress'),
            (Task.Status.BLOCKED, 'Blocked'),
            (Task.Status.DONE, 'Done'),
        ]
        tasks = list(project.tasks.all().order_by('status', 'order', '-updated_at'))
        columns_data = []
        for code, label in columns:
            tasks_for_code = [t for t in tasks if t.status == code]
            columns_data.append((code, label, tasks_for_code))
        ctx['columns_data'] = columns_data
        return ctx

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')
        if task_id and new_status in Task.Status.values:
            task = get_object_or_404(Task, pk=task_id, project=project)
            if ProjectMembership.objects.filter(project=project, user=request.user).exists():
                task.status = new_status
                max_order = Task.objects.filter(project=project, status=new_status).aggregate(Max('order'))['order__max'] or 0
                task.order = max_order + 1
                task.save(update_fields=['status', 'order', 'updated_at'])
        return redirect('projects:board', pk=project.pk)
