# Performance Testing Guide

This directory contains the performance testing scripts for the Salon Booking System using [Locust](https://locust.io/).

## Prerequisites

1.  Install Locust:
    ```bash
    pip install locust
    ```

## Running Tests

### 1. Interactive Mode (Web UI)
This is best for debugging and visual real-time monitoring.

```bash
locust -f performance_tests/locustfile.py
```
*   Open browser at `http://localhost:8089`
*   Set **Host** to your target environment (e.g., `http://localhost:8000` or your staging URL).
*   Set **Number of Users** (e.g., 100).
*   Set **Spawn Rate** (e.g., 10 users/second).

### 2. Headless Mode (CI/CD & Reporting)
This is the "industrial" way to run tests for generating reports without a UI.

```bash
locust -f performance_tests/locustfile.py \
  --headless \
  -u 100 -r 10 \
  --run-time 1m \
  --host http://localhost:8000 \
  --html performance_tests/report.html
```

*   `-u 100`: Simulate 100 concurrent users.
*   `-r 10`: Spawn 10 users per second.
*   `--run-time 1m`: Run the test for 1 minute.
*   `--html report.html`: Generate a professional HTML report.

## Test Scenarios

The `locustfile.py` defines two types of users:

1.  **SalonCustomer (Weight: 3)**
    *   **Health Check (High Freq):** Simulates load balancer pings.
    *   **View Services (Med Freq):** Browsing the catalog.
    *   **View Staff (Low Freq):** Checking availability.
    *   **Attempt Booking (Very Low Freq):** Writing to the database.

2.  **AdminUser (Weight: 1)**
    *   **Generate Report:** Simulates a heavy analytics query.

## Interpreting Results

Open the generated `report.html` to see:
*   **Requests per Second (RPS):** Throughput of your system.
*   **Response Times (ms):** Latency (look at 95th and 99th percentiles).
*   **Failures:** Any non-200 responses.
