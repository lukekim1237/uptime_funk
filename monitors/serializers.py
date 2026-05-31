from rest_framework import serializers
from .models import CheckResult, Monitor


class CheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckResult
        fields = ["id", "checked_at", "status_code", "response_time_ms", "is_up"]


class MonitorSerializer(serializers.ModelSerializer):
    latest_check = serializers.SerializerMethodField()

    class Meta:
        model = Monitor
        fields = ["id", "name", "url", "is_active", "created_at", "latest_check"]

    def get_latest_check(self, obj):
        check = obj.checks.order_by("-checked_at").first()
        if check is None:
            return None
        return {
            "is_up": check.is_up,
            "status_code": check.status_code,
            "response_time_ms": check.response_time_ms,
            "checked_at": check.checked_at,
        }
    