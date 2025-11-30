# Quick Deployment Checklist

Use this as a quick reference while following the full deployment guide.

## ✅ Pre-Deployment Checklist

### AWS Setup

- [ ] AWS account created and logged in
- [ ] Credit card added to account
- [ ] EC2 access confirmed
- [ ] Region selected (note: ******\_******)

### Local Preparation

- [ ] Repository cloned locally
- [ ] Docker installed on local machine
- [ ] Docker Hub account created (username: ******\_******)
- [ ] Gmail App Password generated (password: ******\_******)

### Configuration Values to Prepare

```bash
# Save these values before deployment:

Docker Hub Username:     _________________________
MySQL Root Password:     _________________________
Gmail Email:             _________________________
Gmail App Password:      _________________________
JWT Secret Key:          HdUR4eIHkhAD4RG1srYdSh7B_B3egbM-1Fz86GVVK0k
Control Plane Public IP: _________________________
Worker 1 Public IP:      _________________________
Worker 2 Public IP:      _________________________
```

---

## 🚀 Quick Deployment Steps

### 1. EC2 Instance Creation (15 mins)

- [ ] Launch k8s-control-plane (t3.medium, Ubuntu 22.04)
- [ ] Launch k8s-worker-1 (t3.medium, Ubuntu 22.04)
- [ ] Launch k8s-worker-2 (t3.medium, Ubuntu 22.04)
- [ ] Download .pem key file (salon-k8s-key.pem)
- [ ] Configure security group (ports: 22, 6443, 2379-2380, 10250-10252, 30000-32767, 8001-8006)
- [ ] Assign Elastic IPs (optional)

### 2. Install Software on ALL 3 Instances (20 mins each)

- [ ] SSH to control-plane
- [ ] SSH to worker-1
- [ ] SSH to worker-2
- [ ] Run installation script on each (see Phase 2 in main guide)
- [ ] Verify: `docker --version` and `kubelet --version`

### 3. Initialize Kubernetes Cluster (10 mins)

**On control-plane:**

- [ ] Run `kubeadm init`
- [ ] Copy kubeadm join command (SAVE THIS!)
- [ ] Configure kubectl
- [ ] Install Flannel network

**On workers:**

- [ ] Run saved `kubeadm join` command on worker-1
- [ ] Run saved `kubeadm join` command on worker-2

**Verify:**

- [ ] Run `kubectl get nodes` - see 3 nodes "Ready"

### 4. Build & Push Docker Images (30 mins)

**On local machine:**

- [ ] Login to Docker Hub: `docker login`
- [ ] Build 6 microservice images
- [ ] Push all images to Docker Hub
- [ ] Update image names in k8s/\*.yaml files

### 5. Update Configuration Files (10 mins)

- [ ] Edit k8s/01-secrets.yaml (passwords, JWT key, SMTP)
- [ ] Edit k8s/02-configmap.yaml (DB host, CORS origins)
- [ ] Edit deployment YAMLs (Docker Hub username)

### 6. Deploy to Kubernetes (15 mins)

```bash
# On control-plane, in order:
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-secrets.yaml
kubectl apply -f 02-configmap.yaml
kubectl apply -f 11-mysql-deployment.yaml

# Wait for MySQL to be ready
kubectl wait --for=condition=ready pod -l app=mysql -n salon-booking --timeout=300s

# Initialize database
MYSQL_POD=$(kubectl get pods -n salon-booking -l app=mysql -o jsonpath='{.items[0].metadata.name}')
kubectl cp init-db.sql salon-booking/$MYSQL_POD:/tmp/init-db.sql
kubectl exec -n salon-booking $MYSQL_POD -- mysql -uadmin -p<YOUR-PASSWORD> salon-db < /tmp/init-db.sql

# Deploy all services
kubectl apply -f 03-user-service-deployment.yaml
kubectl apply -f 04-staff-service-deployment.yaml
kubectl apply -f 05-notification-service-deployment.yaml
kubectl apply -f 06-appointment-service-deployment.yaml
kubectl apply -f 07-service-management-deployment.yaml
kubectl apply -f 08-reports-service-deployment.yaml
kubectl apply -f 10-nodeport-services.yaml
```

- [ ] All deployments applied
- [ ] All pods running: `kubectl get pods -n salon-booking`

### 7. Test & Verify (10 mins)

- [ ] Test User Service: `http://<PUBLIC-IP>:30001/docs`
- [ ] Test Service Management: `http://<PUBLIC-IP>:30002/docs`
- [ ] Test Staff Service: `http://<PUBLIC-IP>:30003/docs`
- [ ] Test Appointment Service: `http://<PUBLIC-IP>:30004/docs`
- [ ] Test Reports Service: `http://<PUBLIC-IP>:30005/docs`
- [ ] Test Notification Service: `http://<PUBLIC-IP>:30006/docs`

- [ ] Create test user via API
- [ ] Login with test user
- [ ] Check service logs for errors

---

## 📊 Port Mapping Reference

### Service Ports (Internal)

```
user-service         → 8001
service-management   → 8002
staff-service        → 8003
appointment-service  → 8004
reports-service      → 8005
notification-service → 8006
mysql                → 3306
```

### NodePort (External Access)

```
http://<PUBLIC-IP>:30001 → user-service
http://<PUBLIC-IP>:30002 → service-management
http://<PUBLIC-IP>:30003 → staff-service
http://<PUBLIC-IP>:30004 → appointment-service
http://<PUBLIC-IP>:30005 → reports-service
http://<PUBLIC-IP>:30006 → notification-service
```

---

## 🛠️ Common Commands

### Check Cluster Status

```bash
kubectl get nodes
kubectl get pods -n salon-booking
kubectl get svc -n salon-booking
kubectl get deployments -n salon-booking
```

### View Logs

```bash
kubectl logs -n salon-booking -l app=user-service --tail=50
kubectl logs -n salon-booking -l app=mysql --tail=50
```

### Restart a Service

```bash
kubectl rollout restart deployment user-service -n salon-booking
```

### Scale a Service

```bash
kubectl scale deployment user-service -n salon-booking --replicas=3
```

### Delete Everything and Start Over

```bash
kubectl delete namespace salon-booking
# Then re-apply all manifests
```

### Access MySQL

```bash
MYSQL_POD=$(kubectl get pods -n salon-booking -l app=mysql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it -n salon-booking $MYSQL_POD -- mysql -uadmin -p<PASSWORD> salon-db
```

---

## 🚨 Troubleshooting Quick Fixes

### Pods Not Starting

```bash
kubectl describe pod <POD-NAME> -n salon-booking
kubectl logs <POD-NAME> -n salon-booking
```

### Can't Access NodePort

- Check security group allows ports 30000-32767
- Use PUBLIC IP, not private IP
- Ensure pods are "Running"

### Database Errors

```bash
# Check MySQL is running
kubectl get pods -n salon-booking -l app=mysql

# Verify database exists
kubectl exec -n salon-booking $MYSQL_POD -- mysql -uadmin -p<PASSWORD> -e "SHOW DATABASES;"
```

### Image Pull Errors

- Verify Docker Hub username in YAML files
- Ensure images are pushed: `docker images`
- Make repositories public on Docker Hub

---

## 💰 Cost Management

### Current Configuration Cost (AWS)

- 3× t3.medium: ~$0.0416/hour × 3 = ~$0.125/hour
- **~$90/month if running 24/7**

### Save Money:

```bash
# Stop instances when not in use (AWS Console)
# Restart when needed - data persists on EBS volumes
# Free tier: 750 hours/month of t2.micro (but too small for k8s)
```

---

## 📝 Notes During Deployment

Use this space to write notes:

```
Issue encountered:
_________________________________________________________________
_________________________________________________________________

Solution:
_________________________________________________________________
_________________________________________________________________

Important IPs/Values:
_________________________________________________________________
_________________________________________________________________
```

---

## ✅ Success Criteria

Your deployment is successful when:

- [ ] `kubectl get nodes` shows 3 nodes in "Ready" state
- [ ] `kubectl get pods -n salon-booking` shows all pods "Running"
- [ ] All 6 services accessible via browser at NodePort URLs
- [ ] FastAPI docs visible at each service endpoint
- [ ] Can create a user via API
- [ ] Can login and receive JWT token
- [ ] No error logs in pod logs

**Congratulations! Your microservices are deployed! 🎉**
