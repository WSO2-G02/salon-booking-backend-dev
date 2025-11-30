# Deploy Salon Booking Microservices to Kubernetes
# Using AWS RDS for database

$ErrorActionPreference = "Stop"
$namespace = "salon-booking"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Deploying Salon Booking Microservices to Kubernetes" -ForegroundColor Cyan
Write-Host "Using AWS RDS Database" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if kubectl is available
Write-Host "Checking kubectl availability..." -ForegroundColor Yellow
$kubectlCheck = Get-Command kubectl -ErrorAction SilentlyContinue
if (-not $kubectlCheck) {
    Write-Host "kubectl is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please enable Kubernetes in Docker Desktop: Settings -> Kubernetes -> Enable Kubernetes" -ForegroundColor Yellow
    exit 1
}
Write-Host "kubectl is available" -ForegroundColor Green

Write-Host ""

# Check if Kubernetes is running
Write-Host "Checking Kubernetes cluster connection..." -ForegroundColor Yellow
$clusterTest = kubectl cluster-info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cannot connect to Kubernetes cluster" -ForegroundColor Red
    Write-Host "Please enable Kubernetes in Docker Desktop: Settings -> Kubernetes -> Enable Kubernetes" -ForegroundColor Yellow
    exit 1
}
Write-Host "Connected to Kubernetes cluster" -ForegroundColor Green

Write-Host ""

# Change to k8s directory
$k8sDir = Join-Path $PSScriptRoot "k8s"
if (-not (Test-Path $k8sDir)) {
    Write-Host "k8s directory not found at: $k8sDir" -ForegroundColor Red
    exit 1
}

Push-Location $k8sDir

try {
    # Step 1: Create Namespace
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[1/5] Creating Namespace: $namespace" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    kubectl apply -f 00-namespace.yaml
    if ($LASTEXITCODE -ne 0) { throw "Failed to create namespace" }
    Write-Host "Namespace created successfully" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2

    # Step 2: Create Secrets
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[2/5] Creating Secrets (DB password, JWT secret, SMTP)" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    kubectl apply -f 01-secrets.yaml
    if ($LASTEXITCODE -ne 0) { throw "Failed to create secrets" }
    Write-Host "Secrets created successfully" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2

    # Step 3: Create ConfigMap
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[3/5] Creating ConfigMap (DB config, service URLs)" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    kubectl apply -f 02-configmap.yaml
    if ($LASTEXITCODE -ne 0) { throw "Failed to create configmap" }
    Write-Host "ConfigMap created successfully" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2

    # Step 4: Deploy Microservices
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[4/5] Deploying Microservices" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    
    $services = @(
        @{Name="User Service"; File="03-user-service-deployment.yaml"},
        @{Name="Staff Service"; File="04-staff-service-deployment.yaml"},
        @{Name="Notification Service"; File="05-notification-service-deployment.yaml"},
        @{Name="Appointment Service"; File="06-appointment-service-deployment.yaml"},
        @{Name="Service Management"; File="07-service-management-deployment.yaml"},
        @{Name="Reports Service"; File="08-reports-service-deployment.yaml"}
    )
    
    foreach ($service in $services) {
        Write-Host "Deploying $($service.Name)..." -ForegroundColor Yellow
        kubectl apply -f $service.File
        if ($LASTEXITCODE -ne 0) { throw "Failed to deploy $($service.Name)" }
        Write-Host "$($service.Name) deployed" -ForegroundColor Green
        Start-Sleep -Seconds 1
    }
    
    Write-Host ""
    Write-Host "All microservices deployed successfully" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2

    # Step 5: Deploy NodePort Services for External Access
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[5/5] Creating NodePort Services (External Access)" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    kubectl apply -f 10-nodeport-services.yaml
    if ($LASTEXITCODE -ne 0) { throw "Failed to create NodePort services" }
    Write-Host "NodePort services created successfully" -ForegroundColor Green
    Write-Host ""

    # Wait for pods to be ready
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Waiting for Pods to be Ready (this may take 2-3 minutes)..." -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Pulling Docker images and starting containers..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Show pod status
    Write-Host ""
    Write-Host "Current Pod Status:" -ForegroundColor Yellow
    kubectl get pods -n $namespace
    Write-Host ""
    
    # Wait for all pods to be ready (timeout 5 minutes)
    Write-Host "Waiting for all pods to be ready (timeout: 5 minutes)..." -ForegroundColor Yellow
    $timeout = 300
    $elapsed = 0
    $interval = 10
    
    while ($elapsed -lt $timeout) {
        $notReady = kubectl get pods -n $namespace --no-headers 2>$null | Where-Object { $_ -notmatch "Running.*2/2|Running.*1/1" }
        
        if (-not $notReady) {
            Write-Host "All pods are ready!" -ForegroundColor Green
            break
        }
        
        Write-Host "Waiting... ($elapsed seconds elapsed)" -ForegroundColor Gray
        Start-Sleep -Seconds $interval
        $elapsed += $interval
    }
    
    if ($elapsed -ge $timeout) {
        Write-Host "Warning: Timeout reached. Some pods may not be ready yet." -ForegroundColor Yellow
        Write-Host "Check status with: kubectl get pods -n $namespace" -ForegroundColor Yellow
    }
    
    Write-Host ""

    # Show final deployment status
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Deployment Status" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Pods:" -ForegroundColor Yellow
    kubectl get pods -n $namespace
    Write-Host ""
    
    Write-Host "Services:" -ForegroundColor Yellow
    kubectl get services -n $namespace
    Write-Host ""
    
    Write-Host "Deployments:" -ForegroundColor Yellow
    kubectl get deployments -n $namespace
    Write-Host ""

    # Test health endpoints
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Testing Health Endpoints" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $healthEndpoints = @(
        @{Name="User Service"; Port=30001},
        @{Name="Service Management"; Port=30002},
        @{Name="Staff Service"; Port=30003},
        @{Name="Appointment Service"; Port=30004},
        @{Name="Reports Service"; Port=30005},
        @{Name="Notification Service"; Port=30006}
    )
    
    Write-Host "Waiting 10 seconds for services to stabilize..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
    Write-Host ""
    
    foreach ($endpoint in $healthEndpoints) {
        $url = "http://localhost:$($endpoint.Port)/health"
        Write-Host "Testing $($endpoint.Name) at $url..." -ForegroundColor Yellow -NoNewline
        
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing 2>$null
            if ($response.StatusCode -eq 200) {
                Write-Host " OK" -ForegroundColor Green
            } else {
                Write-Host " Failed (Status: $($response.StatusCode))" -ForegroundColor Red
            }
        } catch {
            Write-Host " Failed (Not responding)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    
    # Success summary
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "Deployment Complete!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Service Access URLs (NodePort):" -ForegroundColor Yellow
    Write-Host "  User Service:         http://localhost:30001" -ForegroundColor White
    Write-Host "  Service Management:   http://localhost:30002" -ForegroundColor White
    Write-Host "  Staff Service:        http://localhost:30003" -ForegroundColor White
    Write-Host "  Appointment Service:  http://localhost:30004" -ForegroundColor White
    Write-Host "  Reports Service:      http://localhost:30005" -ForegroundColor White
    Write-Host "  Notification Service: http://localhost:30006" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Yellow
    Write-Host "  View pods:            kubectl get pods -n $namespace" -ForegroundColor Gray
    Write-Host "  View logs:            kubectl logs <pod-name> -n $namespace" -ForegroundColor Gray
    Write-Host "  Describe pod:         kubectl describe pod <pod-name> -n $namespace" -ForegroundColor Gray
    Write-Host "  Delete deployment:    kubectl delete namespace $namespace" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Database: AWS RDS (database-1.cn8e0eyq896c.eu-north-1.rds.amazonaws.com)" -ForegroundColor Cyan
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "Deployment failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Check pod status: kubectl get pods -n $namespace" -ForegroundColor Gray
    Write-Host "2. View pod logs: kubectl logs <pod-name> -n $namespace" -ForegroundColor Gray
    Write-Host "3. Describe pod: kubectl describe pod <pod-name> -n $namespace" -ForegroundColor Gray
    Write-Host "4. Check events: kubectl get events -n $namespace --sort-by='.lastTimestamp'" -ForegroundColor Gray
    Write-Host ""
    exit 1
} finally {
    Pop-Location
}
