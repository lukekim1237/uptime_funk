import os

from rest_framework import generics, permissions, viewsets

from django.contrib.auth.models import Group, User
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import monitors.serializers as serializers
from monitors.management.commands.run_checks import Command
from monitors.models import CheckResult, Monitor
from monitors.serializers import CheckResultSerializer, MonitorSerializer


# Avoid fragile direct-symbol imports at Django startup.
# If serializers.py fails to import or the attributes are missing, this will raise
# a clearer error instead of a misleading ImportError.
try:
    GroupSerializer = serializers.GroupSerializer
    UserSerializer = serializers.UserSerializer
except AttributeError as e:
    raise ImportError(
        "monitors.serializers did not define GroupSerializer/UserSerializer. "
        "Check that monitors/serializers.py imports cleanly in the deploy environment."
    ) from e


def index(request):
    return render(request, 'monitors/index.html')


@csrf_exempt
def trigger_checks(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    authorization = request.headers.get('Authorization', '')
    cron_secret = os.environ.get('CRON_SECRET', '')


    if authorization != cron_secret:
        return HttpResponseForbidden('Forbidden')

    Command().handle()
    count = Monitor.objects.filter(is_active=True).count()
    return JsonResponse({'checked': count})

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]



class MonitorListCreate(generics.ListCreateAPIView):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # self.request.user represents the logged-in user
        return Monitor.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MonitorDetail(generics.RetrieveDestroyAPIView):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # self.request.user represents the logged-in user
        return Monitor.objects.filter(owner=self.request.user)


class CheckResultList(generics.ListAPIView):
    serializer_class = CheckResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CheckResult.objects.filter(
            monitor_id=self.kwargs['monitor_id'],  # ← matches the URL kwarg
            monitor__owner=self.request.user,
        ).order_by('-result_timestamp')[:20]
    
    # 3637e968e6387d526aba61cb120ba204608acc11