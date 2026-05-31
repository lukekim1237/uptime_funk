from django.contrib import admin
from django.urls import path
from monitors import views
from monitors.views import trigger_checks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path("api/trigger-checks/", trigger_checks, name="trigger_checks"),
]