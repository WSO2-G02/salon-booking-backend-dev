# Kubernetes Deployment Guide - Salon Booking Microservices

## 📋 Overview

This directory contains Kubernetes manifests for deploying the Salon Booking microservices platform.

### Services Included:
- **User Service** (Port 8001) - Authentication & user management
- **Staff Management** (Port 8002) - Staff operations
- **Notification Service** (Port 8003) - Email notifications
- **Appointment Service** (Port 8004) - Booking management
- **Service Management** (Port 8005) - Service catalog
- **Reports & Analytics** (Port 8006) - Business intelligence

---

## 🔧 Configuration Issues Fixed

### ✅ 1. Database Type Consistency
- All services now use **MySQL** (AWS RDS)
- Connection: `mysql+pymysql://user:pass@host:3306/salon-db`

### ✅ 2. Port Conflict Resolution
| Service | Port | Status |
|---------|------|--------|
| User Service | 8001 | ✅ |
| Staff Management | 8002 | ✅ |
| Notification Service | 8003 | ✅ Fixed |
| Appointment Service | 8004 | ✅ |
| Service Management | 8005 | ✅ |
| Reports & Analytics | 8006 | ✅ |

### ✅ 3. Shared JWT Secret
- All services use identical `JWT_SECRET_KEY` from Kubernetes Secret
- Minimum 32 characters required for security
- Configured via `01-secrets.yaml`

---

## 📦 Prerequisites

1. **Kubernetes Cluster** (minikube, EKS, GKE, or AKS)
2. **kubectl** installed and configured
3. **Docker images** built and pushed to registry
4. **NGINX Ingress Controller** installed

### Install NGINX Ingress Controller (if needed):
```bash
# For minikube
minikube addons enable ingress

# For cloud providers
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

---

## 🚀 Quick Start

### Step 1: Update Secrets
Edit `01-secrets.yaml` and replace placeholder values:
```yaml
db-password: "YOUR_ACTUAL_DB_PASSWORD"
jwt-secret-key: "GENERATE_STRONG_SECRET_MIN_32_CHARS"
smtp-username: "your-email@gmail.com"
smtp-password: "your-gmail-app-password"
```

### Step 2: Update ConfigMap
Edit `02-configmap.yaml`:
```yaml
DB_HOST: "your-actual-rds-endpoint.rds.amazonaws.com"
ALLOWED_ORIGINS: "https://yourdomain.com"
```

### Step 3: Build and Push Docker Images
```bash
cd ../

# Build all services
docker build -t your-registry/user-service:latest ./user_service
docker build -t your-registry/staff-service:latest ./staff_management
docker build -t your-registry/notification-service:latest ./notification_service
docker build -t your-registry/appointment-service:latest ./appointment_service
docker build -t your-registry/service-management:latest ./service_management
docker build -t your-registry/reports-service:latest ./reports_analytics

# Push to registry
docker push your-registry/user-service:latest
docker push your-registry/staff-service:latest
docker push your-registry/notification-service:latest
docker push your-registry/appointment-service:latest
docker push your-registry/service-management:latest
docker push your-registry/reports-service:latest
```

### Step 4: Update Image References
Update image names in deployment files (03-08):
```yaml
image: your-registry/user-service:latest  # Change 'salon' to your registry
```

### Step 5: Deploy
```bash
cd k8s

# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows PowerShell
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
```

---

## 🔍 Verification

### Check Pod Status
```bash
kubectl get pods -n salon-booking
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
appointment-service-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
notification-service-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
reports-service-xxxxxxxxxx-xxxxx        1/1     Running   0          2m
service-management-xxxxxxxxxx-xxxxx     1/1     Running   0          2m
staff-service-xxxxxxxxxx-xxxxx          1/1     Running   0          2m
user-service-xxxxxxxxxx-xxxxx           1/1     Running   0          2m
```

### Check Services
```bash
kubectl get services -n salon-booking
```

### Check Ingress
```bash
kubectl get ingress -n salon-booking
```

### View Logs
```bash
# All pods for a service
kubectl logs -n salon-booking -l app=user-service

# Specific pod
kubectl logs -n salon-booking <pod-name>

# Follow logs
kubectl logs -n salon-booking -l app=appointment-service -f
```

### Describe Resources
```bash
kubectl describe pod -n salon-booking <pod-name>
kubectl describe service -n salon-booking user-service
kubectl describe ingress -n salon-booking salon-ingress
```

---

## 🌐 Access Services

### Local Development (minikube)
```bash
# Get minikube IP
minikube ip

# Add to hosts file
# Linux/Mac: /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts
<minikube-ip> salon-api.local

# Access services
curl http://salon-api.local/api/users/health
curl http://salon-api.local/api/appointments/health
```

### Production (Cloud)
1. Configure DNS to point to LoadBalancer IP
2. Update ingress host to your domain
3. Enable HTTPS with cert-manager

---

## 📈 Scaling

### Manual Scaling
```bash
# Scale up appointment service
kubectl scale deployment appointment-service -n salon-booking --replicas=5

# Scale down
kubectl scale deployment appointment-service -n salon-booking --replicas=2
```

### Horizontal Pod Autoscaling
```bash
kubectl autoscale deployment appointment-service -n salon-booking \
  --cpu-percent=70 \
  --min=2 \
  --max=10
```

---

## 🐛 Troubleshooting

### Pod Not Starting
```bash
# Check pod events
kubectl describe pod -n salon-booking <pod-name>

# Check logs
kubectl logs -n salon-booking <pod-name>

# Check previous container logs (if restarting)
kubectl logs -n salon-booking <pod-name> --previous
```

### Service Not Accessible
```bash
# Check endpoints
kubectl get endpoints -n salon-booking

# Check service details
kubectl describe service -n salon-booking <service-name>

# Test from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -n salon-booking -- sh
wget -O- http://user-service:8001/health
```

### Database Connection Issues
```bash
# Check environment variables in pod
kubectl exec -it -n salon-booking <pod-name> -- env | grep DB_

# Test database connectivity
kubectl exec -it -n salon-booking <pod-name> -- sh
```

### Image Pull Errors
```bash
# Check image name
kubectl describe pod -n salon-booking <pod-name> | grep Image

# Create image pull secret (if using private registry)
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n salon-booking

# Add to deployment spec
imagePullSecrets:
  - name: regcred
```

---

## 🔒 Security Best Practices

### Update Secrets
```bash
# Generate strong JWT secret
openssl rand -base64 32

# Update secret
kubectl create secret generic salon-secrets \
  --from-literal=jwt-secret-key='your-new-secret' \
  --dry-run=client -o yaml | kubectl apply -n salon-booking -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment -n salon-booking
```

### Enable Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: salon-network-policy
  namespace: salon-booking
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: salon-booking
```

---

## 🔄 Updates and Rollbacks

### Rolling Update
```bash
# Update image
kubectl set image deployment/user-service \
  user-service=your-registry/user-service:v2 \
  -n salon-booking

# Check rollout status
kubectl rollout status deployment/user-service -n salon-booking
```

### Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/user-service -n salon-booking

# Rollback to specific revision
kubectl rollout undo deployment/user-service --to-revision=2 -n salon-booking

# Check rollout history
kubectl rollout history deployment/user-service -n salon-booking
```

---

## 🧹 Cleanup

### Delete All Resources
```bash
kubectl delete namespace salon-booking
```

### Delete Specific Resources
```bash
kubectl delete deployment <deployment-name> -n salon-booking
kubectl delete service <service-name> -n salon-booking
```

---

## 📊 Monitoring

### Resource Usage
```bash
# Pod resource usage
kubectl top pods -n salon-booking

# Node resource usage
kubectl top nodes
```

### Events
```bash
# Watch events
kubectl get events -n salon-booking --watch

# Filter events
kubectl get events -n salon-booking --field-selector type=Warning
```

---

## 🔗 Service Mesh (Optional)

For advanced features like traffic splitting, circuit breakers, and observability, consider using Istio or Linkerd.

### Install Istio
```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH
istioctl install --set profile=demo -y

# Enable sidecar injection
kubectl label namespace salon-booking istio-injection=enabled
```

---

## 📝 Port Mapping Reference

| Service | Port | Internal DNS | Endpoints |
|---------|------|--------------|-----------|
| User Service | 8001 | user-service:8001 | `/api/users/*` |
| Staff Management | 8002 | staff-service:8002 | `/api/staff/*` |
| Notification Service | 8003 | notification-service:8003 | `/api/notifications/*` |
| Appointment Service | 8004 | appointment-service:8004 | `/api/appointments/*` |
| Service Management | 8005 | service-management:8005 | `/api/services/*` |
| Reports & Analytics | 8006 | reports-service:8006 | `/api/reports/*` |

---

## 📞 Support

For issues or questions:
1. Check pod logs: `kubectl logs -n salon-booking <pod-name>`
2. Check pod events: `kubectl describe pod -n salon-booking <pod-name>`
3. Verify configuration in ConfigMaps and Secrets
4. Ensure database is accessible from cluster

---

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [MySQL on RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_MySQL.html)
