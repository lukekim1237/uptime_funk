from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import CheckResult, Monitor


class CheckResultSerializer(serializers.ModelSerializer):
    checked_at = serializers.DateTimeField(source="result_timestamp", read_only=True)

    class Meta:
        model = CheckResult
        fields = ["id", "checked_at", "status_code", "response_time_ms", "is_up"]


class MonitorSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="monitor_timestamp", read_only=True)
    latest_check = serializers.SerializerMethodField()

    class Meta:
        model = Monitor
        fields = ["id", "name", "url", "is_active", "created_at", "latest_check"]

    def get_latest_check(self, obj):
        check = obj.checks.order_by("-result_timestamp").first()
        if check is None:
            return None
        return {
            "is_up": check.is_up,
            "status_code": check.status_code,
            "response_time_ms": check.response_time_ms,
            "checked_at": check.result_timestamp,
        }


# Simple serializers for the viewsets in `monitors.views`
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "id", "username", "email", "is_staff"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "id", "name"]
