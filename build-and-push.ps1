# Build and Push All Microservices to Docker Hub
# Docker Hub Username: ritzy0717

$ErrorActionPreference = "Stop"
$dockerUsername = "ritzy0717"

# Service configurations: directory -> image name
$services = @{
    "user_service" = "user-service"
    "staff_management" = "staff-service"
    "notification_service" = "notification-service"
    "appointment_service" = "appointment-service"
    "service_management" = "service-management"
    "reports_analytics" = "reports-service"
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Building and Pushing Docker Images to Docker Hub" -ForegroundColor Cyan
Write-Host "Docker Hub Username: $dockerUsername" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Login to Docker Hub
Write-Host "Logging into Docker Hub..." -ForegroundColor Yellow
Write-Host "Please enter your Docker Hub credentials when prompted." -ForegroundColor Gray
docker login
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Hub login failed" -ForegroundColor Red
    exit 1
}
Write-Host "Successfully logged into Docker Hub" -ForegroundColor Green
Write-Host ""

$successCount = 0
$failCount = 0
$totalServices = $services.Count

foreach ($service in $services.GetEnumerator()) {
    $directory = $service.Key
    $imageName = $service.Value
    $fullImageName = "${dockerUsername}/${imageName}:latest"
    
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[$($successCount + $failCount + 1)/$totalServices] Processing: $directory" -ForegroundColor Cyan
    Write-Host "Image: $fullImageName" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    
    # Check if directory exists
    if (-not (Test-Path $directory)) {
        Write-Host "Directory not found: $directory" -ForegroundColor Red
        $failCount++
        continue
    }
    
    # Check if Dockerfile exists
    if (-not (Test-Path "$directory/Dockerfile")) {
        Write-Host "Dockerfile not found in: $directory" -ForegroundColor Red
        $failCount++
        continue
    }
    
    # Build Docker image
    Write-Host ""
    Write-Host "Building image..." -ForegroundColor Yellow
    Push-Location $directory
    try {
        docker build -t $fullImageName .
        if ($LASTEXITCODE -ne 0) {
            throw "Docker build failed"
        }
            Write-Host "Build successful" -ForegroundColor Green
        
        # Push Docker image
        Write-Host ""
        Write-Host "Pushing image to Docker Hub..." -ForegroundColor Yellow
        docker push $fullImageName
        if ($LASTEXITCODE -ne 0) {
            throw "Docker push failed"
        }
        Write-Host "Push successful" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "Failed: $_" -ForegroundColor Red
        $failCount++
    } finally {
        Pop-Location
    }
    
    Write-Host ""
}

# Summary
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Build and Push Summary" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Total Services: $totalServices" -ForegroundColor White
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($successCount -eq $totalServices) {
    Write-Host "All images built and pushed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Verify images at: https://hub.docker.com/u/$dockerUsername" -ForegroundColor Gray
    Write-Host "2. Update k8s/01-secrets.yaml with your credentials" -ForegroundColor Gray
    Write-Host "3. Deploy to Kubernetes: kubectl apply -f k8s/" -ForegroundColor Gray
} else {
    Write-Host "Some images failed to build/push. Please check the errors above." -ForegroundColor Yellow
    exit 1
}
