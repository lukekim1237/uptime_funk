from django.contrib import admin
from django.urls import path, include
from monitors import views
from monitors.views import trigger_checks

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path("api/trigger-checks/", trigger_checks, name="trigger_checks"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]