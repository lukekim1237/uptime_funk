from django.contrib import admin

# Register your models here.
from .models import Monitor, CheckResult


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'owner', 'is_active', 'monitor_timestamp']


@admin.register(CheckResult)
class CheckResultAdmin(admin.ModelAdmin):
    list_display = ['monitor', 'result_timestamp', 'status_code', 'response_time_ms', 'is_up']