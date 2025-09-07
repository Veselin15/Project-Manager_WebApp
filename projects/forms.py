from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Task, ProjectMembership

User = get_user_model()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assignee']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AddCollaboratorForm(forms.Form):
    username = forms.CharField(max_length=150, help_text='Existing username to add as collaborator')
    role = forms.ChoiceField(choices=ProjectMembership.Role.choices, initial=ProjectMembership.Role.MEMBER)

    def clean_username(self):
        uname = self.cleaned_data['username']
        if not User.objects.filter(username=uname).exists():
            raise forms.ValidationError('No such user.')
        return uname
