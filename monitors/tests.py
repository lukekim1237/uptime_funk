from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from .models import Monitor, CheckResult
from django.core.management import call_command


class RunChecksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.monitor = Monitor.objects.create(
            owner=self.user,
            url='https://example.com',
            name='Example'
        )

    @patch('monitors.management.commands.run_checks.requests.get')
    def test_run_checks_creates_check_result(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        call_command('run_checks')

        self.assertEqual(CheckResult.objects.filter(monitor=self.monitor).count(), 1)


class MonitorAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_monitors_returns_401_without_token(self):
        response = self.client.get('/api/monitors/')
        self.assertEqual(response.status_code, 401)


class MonitorIsolationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        Monitor.objects.create(owner=self.user1, url='https://user1site.com', name='User1 Monitor')

    def test_user_cannot_see_another_users_monitors(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/monitors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)