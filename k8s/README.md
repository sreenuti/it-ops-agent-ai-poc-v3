# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the IT Ops Agent System.

## Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured to access your cluster
- Docker image built and pushed to a registry accessible by your cluster

## Deployment Steps

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Create Secrets

**IMPORTANT**: Never commit actual secrets to version control.

```bash
# Copy the template
cp secret.yaml.template secret.yaml

# Edit secret.yaml with your actual values
# Then apply:
kubectl apply -f secret.yaml

# OR create secret directly:
kubectl create secret generic itops-agent-secrets \
  --from-literal=OPENAI_API_KEY=your_key_here \
  --namespace=itops-agent
```

### 3. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 4. Create Persistent Volume Claims

```bash
kubectl apply -f persistentvolumeclaim.yaml
```

**Note**: Adjust `storageClassName` in `persistentvolumeclaim.yaml` based on your cluster's available storage classes.

### 5. Deploy Chroma Database

```bash
kubectl apply -f chroma-deployment.yaml
kubectl apply -f chroma-service.yaml
```

Wait for Chroma to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=chroma -n itops-agent --timeout=300s
```

### 6. Build and Push Docker Image

```bash
# Build the image
docker build -t itops-agent:latest -f docker/Dockerfile .

# Tag for your registry (replace with your registry)
docker tag itops-agent:latest your-registry.com/itops-agent:latest

# Push to registry
docker push your-registry.com/itops-agent:latest

# Update app-deployment.yaml with your image name
```

### 7. Deploy Application

```bash
kubectl apply -f app-deployment.yaml
kubectl apply -f app-service.yaml
```

### 8. (Optional) Deploy Horizontal Pod Autoscaler

```bash
kubectl apply -f hpa.yaml
```

## Verify Deployment

```bash
# Check all resources
kubectl get all -n itops-agent

# Check pod status
kubectl get pods -n itops-agent

# Check logs
kubectl logs -f deployment/itops-agent -n itops-agent

# Check service
kubectl get svc -n itops-agent
```

## Access the Application

### Using LoadBalancer (if supported)

```bash
# Get external IP
kubectl get svc itops-agent-service -n itops-agent

# Access at http://<EXTERNAL_IP>
```

### Using Port Forwarding

```bash
kubectl port-forward svc/itops-agent-service 7860:80 -n itops-agent

# Access at http://localhost:7860
```

### Using NodePort

Change service type in `app-service.yaml` to `NodePort` and access via `<NODE_IP>:<NODE_PORT>`

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n itops-agent

# Check logs
kubectl logs <pod-name> -n itops-agent
```

### Chroma Connection Issues

```bash
# Verify Chroma service is accessible
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://chroma-service:8000/api/v1/heartbeat -n itops-agent
```

### Image Pull Errors

Ensure your image is accessible from the cluster and update `imagePullPolicy` or add image pull secrets.

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n itops-agent

# Check storage class
kubectl get storageclass
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment/itops-agent --replicas=5 -n itops-agent
```

### Automatic Scaling

The HPA (Horizontal Pod Autoscaler) will automatically scale based on CPU and memory usage.

## Updates and Rollouts

```bash
# Update image
kubectl set image deployment/itops-agent itops-agent=itops-agent:v2 -n itops-agent

# Check rollout status
kubectl rollout status deployment/itops-agent -n itops-agent

# Rollback if needed
kubectl rollout undo deployment/itops-agent -n itops-agent
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace itops-agent

# Or delete individually
kubectl delete -f .
```

## Configuration

### Resource Limits

Adjust resource requests and limits in:
- `chroma-deployment.yaml`
- `app-deployment.yaml`

### Storage

Modify storage size in `persistentvolumeclaim.yaml`.

### Service Type

Change service type in `app-service.yaml` based on your access requirements:
- `ClusterIP`: Internal access only
- `NodePort`: Access via node IP
- `LoadBalancer`: External IP (cloud providers)

## Security Considerations

1. **Secrets Management**: Use Kubernetes secrets or external secret management (e.g., AWS Secrets Manager, HashiCorp Vault)
2. **Network Policies**: Implement network policies to restrict pod-to-pod communication
3. **RBAC**: Set up proper Role-Based Access Control
4. **Image Security**: Scan images for vulnerabilities
5. **Resource Limits**: Always set resource limits to prevent resource exhaustion

## Monitoring

Consider adding:
- Prometheus for metrics
- Grafana for visualization
- ELK stack for log aggregation
- AlertManager for alerting

