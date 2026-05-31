import time

import requests
from django.core.management.base import BaseCommand

from monitors.models import CheckResult, Monitor


class Command(BaseCommand):
    help = "Check all active monitors and record results"

    def handle(self, *args, **options):
        # REQUIREMENT 1: Query all Monitor objects where is_active=True
        monitors = Monitor.objects.filter(is_active=True)
        self.stdout.write(f"Checking {monitors.count()} active monitor(s)...")

        # REQUIREMENT 1 (continued): For each one, ...
        for monitor in monitors:
            # REQUIREMENT 4: Handle failures with try/except per monitor
            try:
                # REQUIREMENT 2: Make an HTTP GET with a 10-second timeout
                start = time.monotonic()
                response = requests.get(monitor.url, timeout=10)
                elapsed_ms = (time.monotonic() - start) * 1000

                # REQUIREMENT 3: Record response time in ms, status code, and whether it's up (status < 400) in a new CheckResult
                CheckResult.objects.create(
                    monitor=monitor,
                    status_code=response.status_code,
                    response_time_ms=round(elapsed_ms),
                    is_up=response.status_code < 400,
                )
                self.stdout.write(
                    f"  [{response.status_code}] {monitor.url} — {elapsed_ms:.0f}ms"
                )

            # REQUIREMENT 4 (continued): Handle failures... a failed request still creates a CheckResult with is_up=False and null fields
            except Exception as e:
                CheckResult.objects.create(
                    monitor=monitor,
                    status_code=None,
                    response_time_ms=None,
                    is_up=False,
                )
                self.stdout.write(
                    self.style.ERROR(f"  [FAIL] {monitor.url} — {e}")
                )

        self.stdout.write(self.style.SUCCESS("Done."))

    """
    Local Server vs Render Server
    Error Handling: Displays errors directly in your terminal.Halts the deployment process. You must view the Events or Logs on the Render Dashboard to see errors.
    Environment: Uses your OS, local file paths, and environment variables (.env).Uses production environment variables defined in the Render Dashboard.
    Persistence: hanges to code reload automatically.File changes and runtime files are temporary. A new deploy resets the file system.
    """