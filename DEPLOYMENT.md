# Configuration Issues Resolution & Kubernetes Deployment

## 🔍 Issues Identified and Fixed

### 1. ✅ Database Type Inconsistency (RESOLVED)
**Problem:** Mixed references to MySQL and MSSQL across services  
**Solution:** Standardized all services to use **MySQL (AWS RDS)**
- Updated all `config.py` files to use MySQL
- Database connection: `mysql+pymysql://user:pass@host:3306/salon-db`
- Single shared database: `salon-db`

### 2. ✅ Notification Service Port Conflict (RESOLVED)
**Problem:** Port conflict between notification service (8003) and reports service (8005/8006)  
**Solution:** Standardized port assignments
```
✅ User Service:          8001
✅ Staff Management:      8002
✅ Notification Service:  8003 (FIXED)
✅ Appointment Service:   8004
✅ Service Management:    8005
✅ Reports & Analytics:   8006
```

### 3. ✅ Missing Consistent .env Files (RESOLVED)
**Problem:** No standardized environment configuration across services  
**Solution:** Created `.env.example` files for all 6 services with shared JWT configuration

**CRITICAL:** All services must use the **same JWT_SECRET_KEY** for authentication to work!

---

## 📁 Files Created

### Kubernetes Manifests (`k8s/` directory)
1. `00-namespace.yaml` - Namespace isolation
2. `01-secrets.yaml` - Sensitive data (DB password, JWT secret, SMTP credentials)
3. `02-configmap.yaml` - Non-sensitive configuration
4. `03-user-service-deployment.yaml` - User service deployment & service
5. `04-staff-service-deployment.yaml` - Staff management deployment & service
6. `05-notification-service-deployment.yaml` - Notification service deployment & service
7. `06-appointment-service-deployment.yaml` - Appointment service deployment & service
8. `07-service-management-deployment.yaml` - Service management deployment & service
9. `08-reports-service-deployment.yaml` - Reports & analytics deployment & service
10. `09-ingress.yaml` - API Gateway / Ingress controller
11. `deploy.sh` - Automated deployment script
12. `README.md` - Comprehensive deployment guide

### Environment Configuration Files
1. `.env.template` - Master template for all services
2. `user_service/.env.example` - User service configuration
3. `staff_management/.env.example` - Staff management configuration
4. `notification_service/.env.example` - Notification service configuration
5. `appointment_service/.env.example` - Appointment service configuration
6. `service_management/.env.example` - Service management configuration
7. `reports_analytics/.env.example` - Reports & analytics configuration

---

## 🚀 Next Steps

### 1. Create Actual .env Files
Copy `.env.example` to `.env` in each service directory and update with real values:

```powershell
# PowerShell commands
Copy-Item user_service\.env.example user_service\.env
Copy-Item staff_management\.env.example staff_management\.env
Copy-Item notification_service\.env.example notification_service\.env
Copy-Item appointment_service\.env.example appointment_service\.env
Copy-Item service_management\.env.example service_management\.env
Copy-Item reports_analytics\.env.example reports_analytics\.env
```

### 2. Update Secrets and Configuration

**Critical values to update:**
- `JWT_SECRET_KEY` - Generate strong secret (min 32 chars)
- `DB_HOST` - Your AWS RDS endpoint
- `DB_PASSWORD` - Database password
- `SMTP_USERNAME` & `SMTP_PASSWORD` - Email credentials

**Generate JWT Secret:**
```powershell
# PowerShell - Generate random 32-char string
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 3. Build Docker Images

```powershell
cd C:\Users\User\Desktop\desktop\wso2Project\salon-booking-backend-dev

# Build images
docker build -t salon/user-service:latest ./user_service
docker build -t salon/staff-service:latest ./staff_management
docker build -t salon/notification-service:latest ./notification_service
docker build -t salon/appointment-service:latest ./appointment_service
docker build -t salon/service-management:latest ./service_management
docker build -t salon/reports-service:latest ./reports_analytics
```

### 4. Deploy to Kubernetes

```powershell
cd k8s

# Apply all manifests
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-secrets.yaml
kubectl apply -f 02-configmap.yaml
kubectl apply -f 03-user-service-deployment.yaml
kubectl apply -f 04-staff-service-deployment.yaml
kubectl apply -f 05-notification-service-deployment.yaml
kubectl apply -f 06-appointment-service-deployment.yaml
kubectl apply -f 07-service-management-deployment.yaml
kubectl apply -f 08-reports-service-deployment.yaml
kubectl apply -f 09-ingress.yaml

# Verify deployment
kubectl get pods -n salon-booking
kubectl get services -n salon-booking
```

---

## 🔒 Security Checklist

- [ ] Generate strong JWT secret (min 32 characters)
- [ ] Update database password
- [ ] Configure SMTP credentials
- [ ] Update `01-secrets.yaml` with actual values
- [ ] Update `02-configmap.yaml` with RDS endpoint
- [ ] Ensure all services use **same JWT_SECRET_KEY**
- [ ] Configure CORS allowed origins
- [ ] Enable TLS/HTTPS on ingress (production)

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Ingress Controller                    │
│              (salon-api.local / your-domain)            │
└──────────┬──────────────────────────────────────────────┘
           │
    ┌──────┴────────┐
    │   Namespace:  │
    │ salon-booking │
    └──────┬────────┘
           │
    ┌──────┴─────────────────────────────────────┐
    │                                             │
    ├── User Service (8001)                      │
    ├── Staff Management (8002)                  │
    ├── Notification Service (8003) ✅ Fixed     │
    ├── Appointment Service (8004)               │
    ├── Service Management (8005)                │
    └── Reports & Analytics (8006)               │
           │                                      │
    ┌──────┴────────┐                           │
    │ ConfigMaps &  │                           │
    │   Secrets     │                           │
    └───────────────┘                           │
           │                                     │
    ┌──────┴─────────┐                         │
    │  AWS RDS MySQL │                         │
    │   (salon-db)   │                         │
    └────────────────┘
```

---

## 🔧 Key Features

- **Resource Limits:** Each service has memory (256Mi-512Mi) and CPU (250m-500m) limits
- **Health Checks:** Liveness and readiness probes on `/health` endpoint
- **High Availability:** 2 replicas per service for redundancy
- **Secrets Management:** Sensitive data stored in Kubernetes Secrets
- **Configuration Management:** Non-sensitive config in ConfigMaps
- **Service Discovery:** Internal DNS (service-name:port)
- **API Gateway:** NGINX Ingress for external access

---

## 📞 Troubleshooting

### Pods not starting?
```powershell
kubectl describe pod -n salon-booking <pod-name>
kubectl logs -n salon-booking <pod-name>
```

### Database connection issues?
```powershell
kubectl exec -it -n salon-booking <pod-name> -- env | grep DB_
```

### Service not accessible?
```powershell
kubectl get endpoints -n salon-booking
kubectl describe service -n salon-booking <service-name>
```

---

## ✅ Deployment Verification

After deployment, verify:

1. **All pods running:** `kubectl get pods -n salon-booking`
2. **Services created:** `kubectl get services -n salon-booking`
3. **Ingress configured:** `kubectl get ingress -n salon-booking`
4. **Health checks passing:** `curl http://salon-api.local/api/users/health`

---

## 📚 Documentation

Detailed documentation available in:
- `k8s/README.md` - Kubernetes deployment guide
- `.env.template` - Environment configuration template
- Each service's `.env.example` - Service-specific configuration

---

**Status:** ✅ All configuration issues resolved and Kubernetes manifests created!
