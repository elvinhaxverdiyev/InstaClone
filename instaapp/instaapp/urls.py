from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# Swagger və Redoc üçün Schema View yaradılır
schema_view = get_schema_view(
    openapi.Info(
        title="Comment API",
        default_version='v1',
        description="Bu API şərhləri idarə etmək üçündür",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True, 
    permission_classes=[AllowAny],  
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include("apis.urls")), 
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]

