# Security Policy

## Overview

This document describes the security scanning and CI/CD pipeline for the Salon Booking Backend microservices.

## CI/CD Pipeline Flow

```
Code Push -> Detect Changes -> Unit Tests -> SAST Scan -> Build Image -> Trivy Scan -> Push to ECR -> Update GitOps -> ArgoCD Deploy
```

### Pipeline Stages

| Stage | Description | Tool |
|-------|-------------|------|
| 1. Detect Changes | Identify which services have changed | Git diff |
| 2. Unit Tests | Run pytest on changed services | pytest |
| 3. SAST Scan | Static security analysis of Python code | Bandit |
| 4. Build Image | Build Docker container | Docker Buildx |
| 5. Trivy Scan | Container vulnerability scanning | Trivy |
| 6. Push to ECR | Push image to container registry | AWS ECR |
| 7. Update GitOps | Update deployment manifests | Git |
| 8. Deploy | Sync to Kubernetes | ArgoCD |

## Security Scanning

### Static Application Security Testing (SAST)

- **Tool**: Bandit
- **Trigger**: On every push and pull request
- **Scope**: Python source code in app/ directories
- **Blocking**: No (reports only)

### Container Image Scanning

- **Tool**: Trivy
- **Trigger**: On push to main branch, on pull requests
- **Severity Levels**: CRITICAL, HIGH
- **Blocking**: Yes - builds fail on CRITICAL or HIGH vulnerabilities
- **Results**: Available in GitHub Security tab

### Dependency Scanning

- **Tool**: pip-audit and Trivy filesystem scan
- **Trigger**: On push when requirements.txt changes, weekly schedule (Mondays at 6:00 UTC)
- **Coverage**: All 6 microservices
- **Results**: Visible in GitHub Security tab

### AWS ECR Scanning

- **Tool**: AWS ECR native scanning (scan_on_push enabled)
- **Trigger**: Automatic on image push
- **Note**: Provides additional scanning layer after Trivy

## Unit Testing

- **Framework**: pytest
- **Location**: Each service has a `tests/` directory
- **Configuration**: `pytest.ini` in each service root
- **Coverage**: pytest-cov for code coverage reporting

## Required GitHub Secrets

The following secrets must be configured in GitHub repository settings:

| Secret Name | Description |
|-------------|-------------|
| AWS_ACCESS_KEY_ID | AWS access key for ECR access |
| AWS_SECRET_ACCESS_KEY | AWS secret access key |
| GITOPS_TOKEN | GitHub PAT with repo access to salon-gitops repository |

## Configuration

### AWS Region
- ECR Registry: `024955634588.dkr.ecr.eu-north-1.amazonaws.com`
- Region: `eu-north-1`

### Services
- user_service
- appointment_service
- staff_management
- service_management
- reports_analytics
- notification_service

## Workflow Files

| File | Purpose |
|------|---------|
| `ci-cd-pipeline.yml` | Main CI/CD pipeline with tests, SAST, build, scan, push |
| `dependency-scan.yml` | Scan Python dependencies for vulnerabilities |
