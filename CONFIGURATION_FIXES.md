# Configuration Issues Resolution Summary

## ✅ All Critical Issues FIXED

This document summarizes the configuration fixes applied to prepare the salon booking microservices for Kubernetes deployment on AWS EC2.

---

## Issues Identified and Fixed

### 1. ✅ Port Mismatches Between Code and Kubernetes YAMLs

**Problem:** Kubernetes deployment files had different ports than the Python config.py files.

**Original Incorrect Mapping:**
```
Service               Code Port    K8s Port (OLD)    Status
────────────────────────────────────────────────────────────
User Service          8001        8001              ✅ Match
Service Management    8002        8005              ❌ Wrong
Staff Management      8003        8002              ❌ Wrong
Appointment Service   8004        8004              ✅ Match
Reports & Analytics   8005        8006              ❌ Wrong
Notification Service  8006        8003              ❌ Wrong
```

**Fixed Mapping:**
```
Service               Code Port    K8s Port (NEW)    Status
────────────────────────────────────────────────────────────
User Service          8001        8001              ✅ Fixed
Service Management    8002        8002              ✅ Fixed
Staff Management      8003        8003              ✅ Fixed
Appointment Service   8004        8004              ✅ Fixed
Reports & Analytics   8005        8005              ✅ Fixed
Notification Service  8006        8006              ✅ Fixed
```

**Files Updated:**
- `k8s/04-staff-service-deployment.yaml` - Changed port 8002 → 8003
- `k8s/05-notification-service-deployment.yaml` - Changed port 8003 → 8006
- `k8s/07-service-management-deployment.yaml` - Changed port 8005 → 8002
- `k8s/08-reports-service-deployment.yaml` - Changed port 8006 → 8005
- `k8s/09-ingress.yaml` - Updated all service ports to match

---

### 2. ✅ Notification Service URL Incorrect in Config Files

**Problem:** Services trying to communicate with notification service were using wrong port (8003 instead of 8006).

**Files Fixed:**
- `appointment_service/app/config.py` - Changed URL from `:8003` → `:8006`
- `user_service/app/config.py` - Changed URL from `:8003` → `:8006`
- `staff_management/app/config.py` - Changed URL from `:8003` → `:8006`

**Before:**
```python
NOTIFICATION_SERVICE_URL: str = "http://localhost:8003"
```

**After:**
```python
NOTIFICATION_SERVICE_URL: str = "http://localhost:8006"
```

---

### 3. ✅ ConfigMap Service URLs Updated

**Problem:** Kubernetes ConfigMap had incorrect inter-service URLs.

**File:** `k8s/02-configmap.yaml`

**Fixed:**
```yaml
# OLD (Incorrect)
STAFF_SERVICE_URL: "http://staff-service:8002"
NOTIFICATION_SERVICE_URL: "http://notification-service:8003"
SERVICE_MANAGEMENT_URL: "http://service-management:8005"
REPORTS_SERVICE_URL: "http://reports-service:8006"

# NEW (Correct)
STAFF_SERVICE_URL: "http://staff-service:8003"
NOTIFICATION_SERVICE_URL: "http://notification-service:8006"
SERVICE_MANAGEMENT_URL: "http://service-management:8002"
REPORTS_SERVICE_URL: "http://reports-service:8005"
```

---

### 4. ✅ Database Type Resolved

**Problem:** `.env` file had MSSQL connection string, but all code expects MySQL.

**Original (appointment_service/.env):**
```bash
DATABASE_URL="mssql+pymssql://admin123:user%402025@testdb20251014.database.windows.net:1433/test-db"
```

**Resolution:**
- All services now use MySQL (port 3306) as configured in `config.py`
- Kubernetes uses centralized ConfigMap for DB configuration
- Option to use MySQL in Kubernetes cluster OR AWS RDS MySQL
- Old MSSQL .env file should be deleted - K8s ConfigMap/Secrets are now the source of truth

---

### 5. ✅ Shared JWT Secret Configuration

**Problem:** JWT secret needs to be identical across all 6 services for authentication to work.

**Solution:**
- Centralized JWT secret in `k8s/01-secrets.yaml`
- All services pull from same Kubernetes Secret
- Default value from existing .env preserved: `HdUR4eIHkhAD4RG1srYdSh7B_B3egbM-1Fz86GVVK0k`

**Implementation:**
```yaml
# k8s/01-secrets.yaml
stringData:
  jwt-secret-key: "HdUR4eIHkhAD4RG1srYdSh7B_B3egbM-1Fz86GVVK0k"
```

All deployment YAMLs reference this:
```yaml
- name: JWT_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: salon-secrets
      key: jwt-secret-key
```

---

### 6. ✅ NodePort Services Created for External Access

**Problem:** Original services were ClusterIP only (internal access). EC2 deployment needs external access.

**Solution:** Created `k8s/10-nodeport-services.yaml` with NodePort services.

**Access URLs:**
```
http://<EC2-PUBLIC-IP>:30001  → User Service
http://<EC2-PUBLIC-IP>:30002  → Service Management  
http://<EC2-PUBLIC-IP>:30003  → Staff Service
http://<EC2-PUBLIC-IP>:30004  → Appointment Service
http://<EC2-PUBLIC-IP>:30005  → Reports Service
http://<EC2-PUBLIC-IP>:30006  → Notification Service
```

---

### 7. ✅ MySQL Database Deployment Added

**Problem:** No database deployment in Kubernetes manifests.

**Solution:** Created `k8s/11-mysql-deployment.yaml` with:
- MySQL 8.0 container
- Persistent Volume Claim (10GB)
- Internal service at `mysql-service:3306`
- Health checks and resource limits

---

### 8. ✅ Database Initialization Script Created

**Problem:** No way to create database tables and seed initial data.

**Solution:** Created `k8s/init-db.sql` with:
- All required table schemas (users, sessions, services, staff, staff_availability, appointments)
- Sample data (admin user, 6 services, 3 staff members)
- Proper foreign key relationships

---

### 9. ✅ Placeholder Values Updated in Secrets/ConfigMap

**Problem:** Template values like "your-email@gmail.com" still in configuration files.

**Solution:**
- Updated `k8s/01-secrets.yaml` with actual JWT secret from .env
- Added clear instructions for values user needs to replace
- Set default MySQL password placeholder
- SMTP credentials marked for user to add

**User must update before deployment:**
```yaml
# k8s/01-secrets.yaml
smtp-username: "your-email@gmail.com"        # ← REPLACE
smtp-password: "your-gmail-app-password"     # ← REPLACE
db-password: "YourSecureDBPassword123!"      # ← REPLACE (or keep this)
```

---

## New Files Created

1. **k8s/10-nodeport-services.yaml** - External access to all 6 microservices
2. **k8s/11-mysql-deployment.yaml** - MySQL database with persistent storage
3. **k8s/init-db.sql** - Database schema and seed data
4. **AWS_KUBERNETES_DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
5. **DEPLOYMENT_CHECKLIST.md** - Quick reference checklist
6. **CONFIGURATION_FIXES.md** - This file

---

## Files Modified

### Kubernetes Deployment Files:
1. `k8s/02-configmap.yaml` - Fixed service URLs and added comments
2. `k8s/04-staff-service-deployment.yaml` - Port 8002 → 8003
3. `k8s/05-notification-service-deployment.yaml` - Port 8003 → 8006
4. `k8s/07-service-management-deployment.yaml` - Port 8005 → 8002
5. `k8s/08-reports-service-deployment.yaml` - Port 8006 → 8005
6. `k8s/09-ingress.yaml` - Updated all backend service ports
7. `k8s/01-secrets.yaml` - Added actual JWT secret value

### Application Config Files:
1. `appointment_service/app/config.py` - Fixed notification URL
2. `user_service/app/config.py` - Fixed notification URL
3. `staff_management/app/config.py` - Fixed notification URL

---

## Verification Checklist

Before deploying, verify:

- [x] All K8s deployment YAMLs have correct ports matching config.py
- [x] All health check probes use correct ports
- [x] All Service definitions use correct targetPorts
- [x] ConfigMap has correct inter-service URLs
- [x] Ingress has correct backend ports
- [x] Notification service URL is :8006 in all config files
- [x] JWT secret is centralized in secrets.yaml
- [x] Database deployment exists
- [x] Database init script exists
- [x] NodePort services exist for external access
- [x] All placeholder values are documented

---

## What User Still Needs to Do

### 1. Update k8s/01-secrets.yaml:
```yaml
smtp-username: "your-actual-email@gmail.com"
smtp-password: "your-16-char-gmail-app-password"
db-password: "your-chosen-mysql-password"
```

### 2. Update k8s/02-configmap.yaml:
```yaml
ALLOWED_ORIGINS: "http://localhost:3000,http://<YOUR-EC2-IP>:3000"
# Optionally change DB_HOST if using AWS RDS
```

### 3. Update Docker image names in deployment YAMLs:
```yaml
# Change from:
image: salon/user-service:latest
# To:
image: your-dockerhub-username/user-service:latest
```

### 4. Follow AWS_KUBERNETES_DEPLOYMENT_GUIDE.md step-by-step

---

## Summary

✅ **All critical configuration issues have been resolved!**

The repository is now ready for Kubernetes deployment on AWS EC2. All port mismatches are fixed, services can communicate properly, and comprehensive deployment documentation has been created.

**Next steps:**
1. Review `AWS_KUBERNETES_DEPLOYMENT_GUIDE.md`
2. Update the few remaining placeholder values
3. Follow the deployment guide step-by-step
4. Your microservices will be live on AWS!

**Estimated total deployment time:** 2-3 hours (first time)
