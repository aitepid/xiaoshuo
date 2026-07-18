from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "xiaoshuo-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health", HealthView.as_view(), name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.novels.urls")),
    path("api/v1/", include("apps.bookshelf.urls")),
    path("api/v1/", include("apps.interactions.urls")),
    path("api/v1/", include("apps.ai_gateway.urls")),
]
