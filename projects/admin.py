from django.contrib import admin
from .models import Project, Task, ProjectMembership

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0

class MembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'start_date', 'end_date', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    inlines = [MembershipInline, TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'assignee', 'due_date', 'order', 'updated_at')
    list_filter = ('status', 'priority', 'due_date')
    search_fields = ('title', 'description', 'assignee__username', 'project__name')

@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'added_at')
    search_fields = ('project__name', 'user__username')
    list_filter = ('role',)
