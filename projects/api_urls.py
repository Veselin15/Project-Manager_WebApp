from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='api-projects')
router.register('tasks', TaskViewSet, basename='api-tasks')

urlpatterns = [
    path('', include(router.urls)),
]
