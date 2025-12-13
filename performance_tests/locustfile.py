import logging
from locust import HttpUser, task, between, events
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserServiceCustomer(HttpUser):
    """
    Simulates traffic to the User Service (Port 8001).
    """
    host = "http://localhost:8001"
    wait_time = between(1, 3)
    weight = 2

    def on_start(self):
        logger.info("UserServiceCustomer started session")

    @task(5)
    def health_check(self):
        """Health check ping"""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def get_users(self):
        """Get list of users (may require auth)"""
        with self.client.get("/api/v1/users", catch_response=True) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")


class ServiceManagementCustomer(HttpUser):
    """
    Simulates traffic to the Service Management (Port 8002).
    """
    host = "http://localhost:8002"
    wait_time = between(1, 3)
    weight = 3

    def on_start(self):
        logger.info("ServiceManagementCustomer started session")

    @task(5)
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")

    @task(3)
    def view_services(self):
        """Browse available salon services"""
        with self.client.get("/api/v1/services", catch_response=True) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")


class StaffManagementCustomer(HttpUser):
    """
    Simulates traffic to the Staff Management (Port 8003).
    """
    host = "http://localhost:8003"
    wait_time = between(1, 3)
    weight = 2

    def on_start(self):
        logger.info("StaffManagementCustomer started session")

    @task(5)
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def view_staff(self):
        """Check staff availability"""
        with self.client.get("/api/v1/staff", catch_response=True) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")


class AppointmentServiceCustomer(HttpUser):
    """
    Simulates traffic to the Appointment Service (Port 8004).
    """
    host = "http://localhost:8004"
    wait_time = between(1, 3)
    weight = 3

    def on_start(self):
        logger.info("AppointmentServiceCustomer started session")

    @task(5)
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def view_appointments(self):
        """View appointments"""
        with self.client.get("/api/v1/appointments", catch_response=True) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")


class NotificationServiceCustomer(HttpUser):
    """
    Simulates traffic to the Notification Service (Port 8005).
    """
    host = "http://localhost:8005"
    wait_time = between(1, 3)
    weight = 1

    def on_start(self):
        logger.info("NotificationServiceCustomer started session")

    @task(5)
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")


class ReportsAnalyticsCustomer(HttpUser):
    """
    Simulates traffic to the Reports/Analytics Service (Port 8006).
    """
    host = "http://localhost:8006"
    wait_time = between(2, 5)
    weight = 1

    def on_start(self):
        logger.info("ReportsAnalyticsCustomer started session")

    @task(5)
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")

    @task(1)
    def generate_report(self):
        """Heavy analytics query"""
        with self.client.get("/api/v1/analytics/daily", catch_response=True) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")
