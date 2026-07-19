from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
import os


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "xiaoshuo-api"})


class DiagnosticsView(APIView):
    """诊断 API - 检查系统配置"""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "ok",
            "service": "xiaoshuo-api",
            "environment": {
                "debug": os.getenv('DJANGO_DEBUG', 'False'),
                "allowed_hosts": os.getenv('DJANGO_ALLOWED_HOSTS', '*'),
                "cors_origins": os.getenv('CORS_ALLOWED_ORIGINS', 'Not set'),
                "frontend_url": request.headers.get('origin', 'Unknown'),
            },
            "database": {
                "configured": "Yes" if os.getenv('POSTGRES_HOST') else "No (using default)",
                "host": os.getenv('POSTGRES_HOST', 'localhost'),
            },
            "api_endpoints": {
                "health": "/api/health",
                "auth_register": "/api/v1/auth/register",
                "auth_login": "/api/v1/auth/login",
                "categories": "/api/v1/categories",
                "novels": "/api/v1/novels",
            },
            "debug_info": {
                "request_method": request.method,
                "request_origin": request.headers.get('origin', 'No origin header'),
                "request_host": request.get_host(),
            }
        })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", HealthView.as_view(), name="health"),
    path("api/diagnostics", DiagnosticsView.as_view(), name="diagnostics"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.novels.urls")),
    path("api/v1/", include("apps.bookshelf.urls")),
    path("api/v1/", include("apps.interactions.urls")),
    path("api/v1/", include("apps.ai_gateway.urls")),
]
