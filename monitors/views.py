import os

from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from monitors.management.commands.run_checks import Command
from monitors.models import Monitor

from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from monitors.serializers import GroupSerializer, UserSerializer

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