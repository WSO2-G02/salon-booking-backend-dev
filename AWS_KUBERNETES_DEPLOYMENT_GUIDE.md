# Complete AWS EC2 + Kubernetes Deployment Guide

## Salon Booking Microservices - Manual Setup

This guide walks you through deploying your 6 microservices to AWS EC2 with Kubernetes from scratch.

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Phase 1: AWS EC2 Setup](#phase-1-aws-ec2-setup)
3. [Phase 2: Install Docker & Kubernetes](#phase-2-install-docker--kubernetes)
4. [Phase 3: Create Kubernetes Cluster](#phase-3-create-kubernetes-cluster)
5. [Phase 4: Build & Push Docker Images](#phase-4-build--push-docker-images)
6. [Phase 5: Deploy to Kubernetes](#phase-5-deploy-to-kubernetes)
7. [Phase 6: Verify & Test](#phase-6-verify--test)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need:

- ✅ AWS Account with billing enabled
- ✅ Credit card for EC2 instances (free tier eligible)
- ✅ Gmail account with App Password enabled (for notifications)
- ✅ SSH client (PuTTY for Windows, or built-in terminal)
- ✅ This repository cloned locally

### Skills Required:

- Basic Linux command line knowledge
- Understanding of SSH connections
- Familiarity with text editors (nano/vim)

---

## Phase 1: AWS EC2 Setup

### Step 1.1: Create EC2 Instances

**What we're doing:** Launching 3 Ubuntu servers in AWS - one for Kubernetes master (control plane) and two for workers.

1. **Login to AWS Console**

   - Go to https://console.aws.amazon.com/
   - Login with your AWS account

2. **Navigate to EC2**

   - Search for "EC2" in the top search bar
   - Click "EC2" service

3. **Launch First Instance (Control Plane)**

   - Click orange "Launch Instance" button
   - Configure:
     ```
     Name: k8s-control-plane
     AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
     Instance Type: t3.medium (2 vCPU, 4 GB RAM)
     Key pair: Create new key pair
       - Name: salon-k8s-key
       - Type: RSA
       - Format: .pem (for Mac/Linux) or .ppk (for PuTTY/Windows)
       - DOWNLOAD and save this file securely!
     Network settings:
       - Create security group: k8s-cluster-sg
       - Allow SSH (port 22) from "My IP"
     Storage: 30 GB gp3
     ```
   - Click "Launch Instance"

4. **Launch Worker Nodes (Repeat 2 times)**
   - Click "Launch Instance" again
   - Configure:
     ```
     Name: k8s-worker-1 (then k8s-worker-2)
     AMI: Ubuntu Server 22.04 LTS
     Instance Type: t3.medium
     Key pair: Select "salon-k8s-key" (existing)
     Network settings:
       - Select SAME security group: k8s-cluster-sg
     Storage: 30 GB gp3
     ```
   - Click "Launch Instance"

### Step 1.2: Configure Security Group

**What we're doing:** Opening network ports so Kubernetes nodes can communicate.

1. **Go to Security Groups**

   - In EC2 dashboard, click "Security Groups" in left menu
   - Select "k8s-cluster-sg"
   - Click "Edit inbound rules"

2. **Add These Rules:**

   ```
   Type              Protocol  Port Range    Source              Description
   SSH               TCP       22            My IP               SSH access
   Custom TCP        TCP       6443          Security Group ID   Kubernetes API
   Custom TCP        TCP       2379-2380     Security Group ID   etcd
   Custom TCP        TCP       10250-10252   Security Group ID   Kubelet
   Custom TCP        TCP       30000-32767   0.0.0.0/0           NodePort Services
   Custom TCP        TCP       8001-8006     0.0.0.0/0           Microservices (testing)
   All traffic       All       All           Security Group ID   Inter-node communication
   ```

3. **Save Rules**

### Step 1.3: Assign Elastic IPs (Optional but Recommended)

**What we're doing:** Getting permanent IP addresses that won't change if we restart instances.

1. **Allocate Elastic IPs**

   - In EC2 dashboard, click "Elastic IPs" in left menu
   - Click "Allocate Elastic IP address" → Allocate
   - Repeat 3 times (one for each instance)

2. **Associate IPs to Instances**

   - Select first Elastic IP → Actions → Associate Elastic IP address
   - Select "k8s-control-plane" instance → Associate
   - Repeat for worker-1 and worker-2

3. **Note Down IPs:**
   ```
   Control Plane IP: _________________
   Worker 1 IP:      _________________
   Worker 2 IP:      _________________
   ```

---

## Phase 2: Install Docker & Kubernetes

**What we're doing:** Installing all required software on each EC2 instance.

### Step 2.1: Connect to Each Instance

**For Windows (using PuTTY):**

1. Open PuTTYgen → Load your .ppk key
2. Open PuTTY
3. Host: `ubuntu@<EC2-PUBLIC-IP>`
4. Connection → SSH → Auth → Browse and select .ppk file
5. Click "Open"

**For Mac/Linux:**

```bash
chmod 400 salon-k8s-key.pem
ssh -i salon-k8s-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### Step 2.2: Install on ALL 3 Instances

**Run these commands on each instance (control plane + both workers):**

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Disable swap (Kubernetes requirement)
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# 3. Load kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# 4. Configure sysctl
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system

# 5. Install Docker
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 6. Configure containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd

# 7. Add Kubernetes repository
sudo apt install -y apt-transport-https
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

# 8. Install Kubernetes components (v1.28)
sudo apt update
sudo apt install -y kubelet=1.28.0-1.1 kubeadm=1.28.0-1.1 kubectl=1.28.0-1.1
sudo apt-mark hold kubelet kubeadm kubectl

# 9. Enable kubelet
sudo systemctl enable kubelet

# Verify installation
docker --version
kubelet --version
kubeadm version
```

**Expected output:**

```
Docker version 24.x.x
Kubernetes v1.28.0
```

---

## Phase 3: Create Kubernetes Cluster

### Step 3.1: Initialize Control Plane

**Run ONLY on control-plane instance:**

```bash
# Get the PRIVATE IP of control plane
CONTROL_PLANE_IP=$(hostname -I | awk '{print $1}')
echo "Control Plane IP: $CONTROL_PLANE_IP"

# Initialize cluster
sudo kubeadm init \
  --apiserver-advertise-address=$CONTROL_PLANE_IP \
  --pod-network-cidr=10.244.0.0/16 \
  --control-plane-endpoint=$CONTROL_PLANE_IP

# IMPORTANT: Copy the entire "kubeadm join" command that appears!
# It looks like:
# kubeadm join <IP>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
# Save this to a text file!
```

### Step 3.2: Configure kubectl

**Still on control-plane:**

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Verify
kubectl get nodes
# You should see: k8s-control-plane   NotReady   control-plane   1m   v1.28.0
```

### Step 3.3: Install Pod Network (Flannel)

**Still on control-plane:**

```bash
# Install Flannel CNI
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# Wait 30 seconds, then check
kubectl get pods -n kube-flannel

# Wait until all pods show "Running"
```

### Step 3.4: Join Worker Nodes

**Run on BOTH worker instances (worker-1 and worker-2):**

```bash
# Paste the "kubeadm join" command you saved earlier
# It should look like:
sudo kubeadm join <CONTROL-PLANE-PRIVATE-IP>:6443 \
  --token <your-token> \
  --discovery-token-ca-cert-hash sha256:<your-hash>
```

**Expected output:**

```
This node has joined the cluster:
* Certificate signing request was sent to apiserver and a response was received.
* The Kubelet was informed of the new secure connection details.
```

### Step 3.5: Verify Cluster

**Back on control-plane:**

```bash
kubectl get nodes

# You should see all 3 nodes in "Ready" state:
# NAME                STATUS   ROLES           AGE   VERSION
# k8s-control-plane   Ready    control-plane   5m    v1.28.0
# k8s-worker-1        Ready    <none>          2m    v1.28.0
# k8s-worker-2        Ready    <none>          2m    v1.28.0
```

🎉 **Kubernetes cluster is ready!**

---

## Phase 4: Build & Push Docker Images

**What we're doing:** Creating Docker images for all 6 microservices and making them available to Kubernetes.

### Step 4.1: Install Docker on Your Local Machine

**Skip if already installed.**

- Windows/Mac: Download Docker Desktop from https://www.docker.com/products/docker-desktop
- Linux: Already installed in Phase 2

### Step 4.2: Create Docker Hub Account (Free)

1. Go to https://hub.docker.com/
2. Sign up for free account
3. Note your username: `__________________`

### Step 4.3: Build Images Locally

**On your local machine (where you have the code):**

```bash
# Navigate to project directory
cd salon-booking-backend-dev

# Login to Docker Hub
docker login
# Enter your Docker Hub username and password

# Set your Docker Hub username
export DOCKER_USERNAME=your-dockerhub-username

# Build all 6 microservices
docker build -t $DOCKER_USERNAME/user-service:latest ./user_service
docker build -t $DOCKER_USERNAME/service-management:latest ./service_management
docker build -t $DOCKER_USERNAME/staff-service:latest ./staff_management
docker build -t $DOCKER_USERNAME/appointment-service:latest ./appointment_service
docker build -t $DOCKER_USERNAME/reports-service:latest ./reports_analytics
docker build -t $DOCKER_USERNAME/notification-service:latest ./notification_service

# Push to Docker Hub
docker push $DOCKER_USERNAME/user-service:latest
docker push $DOCKER_USERNAME/service-management:latest
docker push $DOCKER_USERNAME/staff-service:latest
docker push $DOCKER_USERNAME/appointment-service:latest
docker push $DOCKER_USERNAME/reports-service:latest
docker push $DOCKER_USERNAME/notification-service:latest
```

**Alternative: Build on EC2 Control Plane**

```bash
# SSH to control plane
# Install git
sudo apt install -y git

# Clone your repository
git clone https://github.com/WSO2-G02/salon-booking-backend-dev.git
cd salon-booking-backend-dev

# Build images (same commands as above)
```

### Step 4.4: Update Kubernetes YAML Files

**Edit all deployment files to use your Docker Hub images:**

```bash
# On control plane or local machine
cd k8s

# Edit each deployment file and replace 'salon/' with your username
# Files to edit:
# - 03-user-service-deployment.yaml
# - 04-staff-service-deployment.yaml
# - 05-notification-service-deployment.yaml
# - 06-appointment-service-deployment.yaml
# - 07-service-management-deployment.yaml
# - 08-reports-service-deployment.yaml

# Change this line in each file:
# FROM: image: salon/user-service:latest
# TO:   image: YOUR-DOCKERHUB-USERNAME/user-service:latest
```

---

## Phase 5: Deploy to Kubernetes

**What we're doing:** Deploying all microservices to the Kubernetes cluster.

### Step 5.1: Transfer Kubernetes Manifests to Control Plane

**Option A: Using git (easiest):**

```bash
# On control plane
cd ~
git clone https://github.com/WSO2-G02/salon-booking-backend-dev.git
cd salon-booking-backend-dev/k8s
```

**Option B: Using SCP:**

```bash
# On your local machine
scp -i salon-k8s-key.pem -r k8s ubuntu@<CONTROL-PLANE-IP>:~/
```

### Step 5.2: Update Configuration Files

**On control plane:**

```bash
cd ~/salon-booking-backend-dev/k8s

# Edit secrets (IMPORTANT!)
nano 01-secrets.yaml
```

**Update these values:**

```yaml
stringData:
  db-password: "YourStrongPassword123!" # Choose a strong password
  jwt-secret-key: "HdUR4eIHkhAD4RG1srYdSh7B_B3egbM-1Fz86GVVK0k" # Keep this or generate new
  smtp-username: "your-actual-email@gmail.com" # Your Gmail
  smtp-password: "your-gmail-app-password" # Get from Google Account settings
```

**To get Gmail App Password:**

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Search for "App passwords"
4. Generate new app password for "Mail"
5. Copy the 16-character password

```bash
# Edit ConfigMap
nano 02-configmap.yaml
```

**Update these values:**

```yaml
data:
  DB_HOST: "mysql-service" # Keep this if using in-cluster MySQL
  # OR if using AWS RDS:
  # DB_HOST: "your-rds-endpoint.us-east-1.rds.amazonaws.com"

  ALLOWED_ORIGINS: "http://localhost:3000,http://<YOUR-CONTROL-PLANE-PUBLIC-IP>:3000"
```

### Step 5.3: Deploy in Order

```bash
# 1. Create namespace
kubectl apply -f 00-namespace.yaml
kubectl get namespace salon-booking

# 2. Create secrets
kubectl apply -f 01-secrets.yaml
kubectl get secrets -n salon-booking

# 3. Create ConfigMap
kubectl apply -f 02-configmap.yaml
kubectl get configmap -n salon-booking

# 4. Deploy MySQL database
kubectl apply -f 11-mysql-deployment.yaml

# Wait for MySQL to be ready (takes 2-3 minutes)
kubectl wait --for=condition=ready pod -l app=mysql -n salon-booking --timeout=300s

# 5. Initialize database
# Get MySQL pod name
MYSQL_POD=$(kubectl get pods -n salon-booking -l app=mysql -o jsonpath='{.items[0].metadata.name}')

# Copy SQL script to pod
kubectl cp init-db.sql salon-booking/$MYSQL_POD:/tmp/init-db.sql

# Execute SQL script
kubectl exec -n salon-booking $MYSQL_POD -- mysql -uadmin -pYourStrongPassword123! salon-db < /tmp/init-db.sql

# 6. Deploy all microservices
kubectl apply -f 03-user-service-deployment.yaml
kubectl apply -f 04-staff-service-deployment.yaml
kubectl apply -f 05-notification-service-deployment.yaml
kubectl apply -f 06-appointment-service-deployment.yaml
kubectl apply -f 07-service-management-deployment.yaml
kubectl apply -f 08-reports-service-deployment.yaml

# 7. Create NodePort services for external access
kubectl apply -f 10-nodeport-services.yaml

# 8. (Optional) Deploy Ingress controller
kubectl apply -f 09-ingress.yaml
```

### Step 5.4: Monitor Deployment

```bash
# Watch all pods starting up
kubectl get pods -n salon-booking -w

# Wait until all pods show "Running" and "2/2" ready
# Press Ctrl+C to exit watch mode

# Check services
kubectl get svc -n salon-booking

# Check deployments
kubectl get deployments -n salon-booking
```

**Expected output:**

```
NAME                    READY   STATUS    RESTARTS   AGE
mysql-...               1/1     Running   0          5m
user-service-...        1/1     Running   0          2m
staff-service-...       1/1     Running   0          2m
notification-service... 1/1     Running   0          2m
appointment-service...  1/1     Running   0          2m
service-management-...  1/1     Running   0          2m
reports-service-...     1/1     Running   0          2m
```

---

## Phase 6: Verify & Test

### Step 6.1: Access Services via NodePort

**Get your control plane PUBLIC IP:**

```bash
# Your services are now accessible at:
http://<CONTROL-PLANE-PUBLIC-IP>:30001  # User Service
http://<CONTROL-PLANE-PUBLIC-IP>:30002  # Service Management
http://<CONTROL-PLANE-PUBLIC-IP>:30003  # Staff Service
http://<CONTROL-PLANE-PUBLIC-IP>:30004  # Appointment Service
http://<CONTROL-PLANE-PUBLIC-IP>:30005  # Reports Service
http://<CONTROL-PLANE-PUBLIC-IP>:30006  # Notification Service
```

### Step 6.2: Test Each Service

**Open your browser and visit:**

```
http://<CONTROL-PLANE-PUBLIC-IP>:30001/docs
```

You should see **FastAPI Swagger documentation**!

**Test user registration:**

```bash
curl -X POST http://<CONTROL-PLANE-PUBLIC-IP>:30001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "phone": "1234567890"
  }'
```

**Test user login:**

```bash
curl -X POST http://<CONTROL-PLANE-PUBLIC-IP>:30001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

### Step 6.3: Verify Inter-Service Communication

```bash
# Check logs for notification service
kubectl logs -n salon-booking -l app=notification-service --tail=50

# Check logs for user service
kubectl logs -n salon-booking -l app=user-service --tail=50

# If you see database connection errors, check MySQL:
kubectl logs -n salon-booking -l app=mysql --tail=50
```

### Step 6.4: Test Database Connection

```bash
# Connect to MySQL pod
kubectl exec -it -n salon-booking <MYSQL-POD-NAME> -- mysql -uadmin -pYourStrongPassword123! salon-db

# Run queries
SELECT * FROM users;
SELECT * FROM services;
SELECT * FROM staff;

# Exit
exit
```

---

## Troubleshooting

### Issue: Pods Stuck in "Pending" State

```bash
# Check pod events
kubectl describe pod <POD-NAME> -n salon-booking

# Common causes:
# - Insufficient resources → Use smaller instance types or reduce replicas
# - Image pull errors → Check Docker Hub username in YAML files
```

### Issue: Pods in "CrashLoopBackOff"

```bash
# Check logs
kubectl logs <POD-NAME> -n salon-booking

# Common causes:
# - Database connection failed → Check MySQL is running
# - Missing environment variables → Check secrets and configmap
# - Wrong JWT_SECRET_KEY → Ensure it matches across all services
```

### Issue: Can't Access Services via NodePort

```bash
# Check security group allows ports 30000-32767
# Check NodePort services are created:
kubectl get svc -n salon-booking | grep NodePort

# Get exact NodePort:
kubectl get svc user-service-nodeport -n salon-booking -o yaml | grep nodePort
```

### Issue: Database Connection Errors

```bash
# Check MySQL is running
kubectl get pods -n salon-booking -l app=mysql

# Check MySQL logs
kubectl logs -n salon-booking -l app=mysql

# Verify password matches in secrets:
kubectl get secret salon-secrets -n salon-booking -o yaml
# Look for db-password (it's base64 encoded)
echo "<base64-password>" | base64 -d
```

### Issue: Services Can't Talk to Each Other

```bash
# Check internal DNS resolution
kubectl run -it --rm debug --image=busybox -n salon-booking -- nslookup user-service

# Verify service endpoints:
kubectl get endpoints -n salon-booking
```

---

## Next Steps

### Production Improvements:

1. **Set up HTTPS/SSL**

   - Install cert-manager
   - Get Let's Encrypt certificates
   - Configure Ingress with TLS

2. **Use AWS RDS for MySQL**

   - More reliable than in-cluster MySQL
   - Automated backups
   - Update `DB_HOST` in ConfigMap

3. **Add Monitoring**

   - Install Prometheus & Grafana
   - Monitor resource usage
   - Set up alerts

4. **Implement CI/CD**

   - GitHub Actions for automated builds
   - Auto-deploy on git push
   - Rolling updates

5. **Scale Services**
   ```bash
   kubectl scale deployment user-service -n salon-booking --replicas=3
   ```

---

## Summary

✅ **You've successfully:**

- Created a 3-node Kubernetes cluster on AWS EC2
- Installed Docker and Kubernetes (kubeadm)
- Deployed 6 microservices with proper configuration
- Set up MySQL database
- Exposed services via NodePort
- Verified all services are running and communicating

**Your microservices are now live at:**

```
User Service:        http://<PUBLIC-IP>:30001/docs
Service Management:  http://<PUBLIC-IP>:30002/docs
Staff Service:       http://<PUBLIC-IP>:30003/docs
Appointment Service: http://<PUBLIC-IP>:30004/docs
Reports Service:     http://<PUBLIC-IP>:30005/docs
Notification Service:http://<PUBLIC-IP>:30006/docs
```

**Cost Estimate (AWS):**

- 3× t3.medium instances: ~$75/month
- 30GB EBS storage: ~$3/month
- **Total: ~$78/month** (stop instances when not in use to save money)

**To stop instances:**

```bash
# From AWS Console: EC2 → Instances → Select all → Instance State → Stop
```

---

## Questions?

If you encounter issues:

1. Check the Troubleshooting section above
2. Run: `kubectl get events -n salon-booking --sort-by='.lastTimestamp'`
3. Check pod logs: `kubectl logs <POD-NAME> -n salon-booking`
