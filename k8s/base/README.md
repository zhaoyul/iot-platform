# Kubernetes Configuration

## Base Configuration

The base manifests provide a starting point for deploying the IoT Platform on Kubernetes.

### Before Deploying

1. **Update Domain Names**: Edit `ingress.yaml` to replace the example domains:
   - `git.iot-platform.com` → your actual Git service domain
   - `api.iot-platform.com` → your actual API domain
   - `viz.iot-platform.com` → your actual visualization domain

2. **Configure Secrets**: Update the PostgreSQL password in `postgres.yaml`:
   ```bash
   # Generate a secure password
   echo -n "your-secure-password" | base64
   # Update the password field in postgres-secret
   ```

3. **Storage Classes**: Ensure your cluster has a default storage class or specify one in the PVC definitions.

4. **TLS Certificates**: If using cert-manager, ensure it's installed and configured:
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

## Deployment

```bash
# Create namespace
kubectl create namespace iot-platform

# Apply base configuration
kubectl apply -k . -n iot-platform

# Check deployment status
kubectl get pods -n iot-platform
kubectl get svc -n iot-platform
kubectl get ingress -n iot-platform
```

## Overlays

Use overlays for environment-specific configurations:

### Development
```bash
kubectl apply -k ../overlays/dev -n iot-platform
```

### Production
```bash
kubectl apply -k ../overlays/prod -n iot-platform
```

## Scaling

To scale services:
```bash
kubectl scale deployment gitea --replicas=3 -n iot-platform
```

Note: Gitea requires additional configuration for multi-replica deployment (shared storage, database sessions).

## Monitoring

Access Prometheus and Grafana:
```bash
kubectl port-forward svc/prometheus 9090:9090 -n iot-platform
kubectl port-forward svc/grafana 3000:3000 -n iot-platform
```

## Troubleshooting

View logs:
```bash
kubectl logs -f deployment/gitea -n iot-platform
kubectl logs -f deployment/git-parser -n iot-platform
kubectl logs -f deployment/asset-manager -n iot-platform
```

Check events:
```bash
kubectl get events -n iot-platform --sort-by='.lastTimestamp'
```
