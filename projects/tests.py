from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Project, Task, ProjectMembership

User = get_user_model()

class AccessTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass12345')
        self.member = User.objects.create_user(username='member', password='pass12345')
        self.other = User.objects.create_user(username='other', password='pass12345')

        self.project = Project.objects.create(owner=self.owner, name='Proj')
        ProjectMembership.objects.create(project=self.project, user=self.owner, role=ProjectMembership.Role.OWNER)
        ProjectMembership.objects.create(project=self.project, user=self.member, role=ProjectMembership.Role.MEMBER)
        Task.objects.create(project=self.project, title='T1')

    def test_list_shows_only_member_projects(self):
        self.client.login(username='member', password='pass12345')
        resp = self.client.get(reverse('projects:project_list'))
        self.assertContains(resp, 'Proj')
        self.client.logout()
        self.client.login(username='other', password='pass12345')
        resp = self.client.get(reverse('projects:project_list'))
        self.assertNotContains(resp, 'Proj')
