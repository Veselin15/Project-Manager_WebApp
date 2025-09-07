from django.contrib import admin
from django.urls import path, include
from projects.views import SignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('api/', include('projects.api_urls')),
    path('', include(('projects.urls', 'projects'), namespace='projects')),
]
