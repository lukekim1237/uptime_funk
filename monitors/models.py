from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Monitor(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    # creating a database relationship linking a specific model to the built-in User model
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    monitor_timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class CheckResult(models.Model):
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE, related_name='checks')
    result_timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField(null=True)
    response_time_ms = models.IntegerField(null=True)
    is_up = models.BooleanField()
    def __str__(self):
        return f"{self.monitor.name} - {self.result_timestamp} - {'UP' if self.is_up else 'DOWN'}"