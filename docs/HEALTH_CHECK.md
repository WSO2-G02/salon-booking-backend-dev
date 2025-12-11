# Health Check Endpoint

## Table of Contents

1. [Overview](#overview)
2. [Endpoint Specification](#endpoint-specification)
3. [Response Format](#response-format)
4. [Kubernetes Integration](#kubernetes-integration)
5. [Architecture](#architecture)

---

## Overview

All microservices expose a `/health` endpoint for Kubernetes health monitoring. This endpoint verifies application and database connectivity, enabling automatic traffic management and pod recovery.

---

## Endpoint Specification

| Property | Value |
|----------|-------|
| Path | `/health` |
| Method | `GET` |
| Authentication | None |
| Response Type | `application/json` |

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Service healthy, database connected |
| 503 | Service Unavailable | Service unhealthy, database disconnected |

---

## Response Format

### Healthy Response (200 OK)

```json
{
  "service": "user_service",
  "status": "healthy",
  "checks": {
    "database": "connected"
  }
}
```

### Unhealthy Response (503 Service Unavailable)

```json
{
  "service": "user_service",
  "status": "unhealthy",
  "checks": {
    "database": "disconnected"
  }
}
```

---

## Kubernetes Integration

The health endpoint is used by two Kubernetes probes:

```mermaid
flowchart LR
    subgraph Kubernetes
        RP[Readiness Probe]
        LP[Liveness Probe]
    end

    subgraph Pod
        APP[FastAPI App]
        DB[(Database)]
    end

    RP -->|GET /health| APP
    LP -->|GET /health| APP
    APP -->|SELECT 1| DB
```

### Readiness Probe

Determines if the pod should receive traffic.

| Parameter | Value | Description |
|-----------|-------|-------------|
| initialDelaySeconds | 5 | Wait before first check |
| periodSeconds | 10 | Check interval |
| failureThreshold | 3 | Failures before removal |

**Behavior:** Pod removed from Service after 3 consecutive failures (30s).

### Liveness Probe

Determines if the pod should be restarted.

| Parameter | Value | Description |
|-----------|-------|-------------|
| initialDelaySeconds | 15 | Wait before first check |
| periodSeconds | 20 | Check interval |
| failureThreshold | 3 | Failures before restart |

**Behavior:** Pod restarted after 3 consecutive failures (60s).

---

## Architecture

### Health Check Flow

```mermaid
sequenceDiagram
    participant K8s as Kubernetes
    participant App as FastAPI
    participant DB as MySQL

    loop Every 10s (Readiness) / 20s (Liveness)
        K8s->>App: GET /health
        App->>DB: SELECT 1
        alt Database Connected
            DB-->>App: OK
            App-->>K8s: 200 OK
        else Database Disconnected
            DB-->>App: Error
            App-->>K8s: 503 Unavailable
        end
    end
```

### Automatic Recovery Flow

```mermaid
flowchart TB
    A[Health Check Fails] --> B{Which Probe?}
    
    B -->|Readiness| C[Remove from Service]
    C --> D[No new traffic]
    D --> E[Pod stays running]
    E --> F[Can recover on its own]
    
    B -->|Liveness| G[Restart Pod]
    G --> H[New container starts]
    H --> I[Fresh database connection]
```

---

## Service Ports

| Service | Port |
|---------|------|
| user_service | 8001 |
| service_management | 8002 |
| staff_management | 8003 |
| appointment_service | 8004 |
| notification_service | 8005 |
| reports_analytics | 8006 |
