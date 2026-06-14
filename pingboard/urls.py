from django.contrib import admin
from django.urls import path, include
from monitors import views
from monitors.views import trigger_checks
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/trigger-checks/", trigger_checks, name="trigger_checks"),
    path("api/token-auth/", obtain_auth_token, name="api_token_auth"),
    path("api/", include("monitors.urls")),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path('', views.login_page, name='login'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
]