from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('financeapp.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    # Serve the main application HTML
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
]
