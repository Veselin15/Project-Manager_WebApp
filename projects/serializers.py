from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Project, Task, ProjectMembership

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)

    class Meta:
        model = ProjectMembership
        fields = ['id', 'project', 'user', 'user_id', 'role', 'added_at']
        read_only_fields = ['id', 'added_at']

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    memberships = ProjectMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'status', 'start_date', 'end_date', 'owner', 'memberships', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='assignee', write_only=True, allow_null=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'project', 'title', 'description', 'status', 'priority', 'due_date', 'assignee', 'assignee_id', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
