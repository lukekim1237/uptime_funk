from django.urls import path
from monitors import views

urlpatterns = [
    path("monitors/", views.MonitorListCreate.as_view(), name="monitor-list-create"),
    path("monitors/<int:pk>/", views.MonitorDetail.as_view(), name="monitor-detail"),
    path("monitors/<int:monitor_id>/checks/", views.CheckResultList.as_view(), name="monitor-checks"),
]