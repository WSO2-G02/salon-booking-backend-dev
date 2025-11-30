#!/bin/bash

echo "🚀 Deploying Salon Booking Microservices to Kubernetes..."
echo ""

# Apply manifests in order
echo "📦 Creating namespace..."
kubectl apply -f 00-namespace.yaml

echo ""
echo "🔐 Creating secrets..."
kubectl apply -f 01-secrets.yaml

echo ""
echo "⚙️  Creating configmaps..."
kubectl apply -f 02-configmap.yaml

echo ""
echo "🔧 Deploying services..."
kubectl apply -f 03-user-service-deployment.yaml
kubectl apply -f 04-staff-service-deployment.yaml
kubectl apply -f 05-notification-service-deployment.yaml
kubectl apply -f 06-appointment-service-deployment.yaml
kubectl apply -f 07-service-management-deployment.yaml
kubectl apply -f 08-reports-service-deployment.yaml

echo ""
echo "🌐 Creating ingress..."
kubectl apply -f 09-ingress.yaml

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Check status with:"
echo "  kubectl get pods -n salon-booking"
echo "  kubectl get services -n salon-booking"
echo "  kubectl get ingress -n salon-booking"
echo ""
echo "🔍 View logs:"
echo "  kubectl logs -n salon-booking -l app=user-service"
echo "  kubectl logs -n salon-booking -l app=appointment-service"
