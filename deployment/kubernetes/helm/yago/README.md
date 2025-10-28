# YAGO Helm Chart

Official Helm chart for deploying YAGO (Yet Another Graph Orchestrator) on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure
- Ingress controller (NGINX recommended)

## Installing the Chart

### Quick Start

```bash
# Add the YAGO Helm repository (if published)
helm repo add yago https://charts.yago.dev
helm repo update

# Install YAGO
helm install yago yago/yago --namespace yago --create-namespace
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/yago.git
cd yago/deployment/kubernetes/helm

# Install
helm install yago ./yago --namespace yago --create-namespace
```

### With Custom Values

```bash
# Create your values file
cat > my-values.yaml <<EOF
ingress:
  enabled: true
  hosts:
    - host: yago.mydomain.com
      paths:
        - path: /api
          pathType: Prefix
          backend: backend
        - path: /
          pathType: Prefix
          backend: frontend

secrets:
  openaiApiKey: "sk-your-actual-key"
  anthropicApiKey: "sk-ant-your-actual-key"

backend:
  replicaCount: 5

frontend:
  replicaCount: 3
EOF

# Install with custom values
helm install yago ./yago -f my-values.yaml --namespace yago --create-namespace
```

## Uninstalling the Chart

```bash
helm uninstall yago --namespace yago
```

## Configuration

The following table lists the configurable parameters and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `namespace` | Kubernetes namespace | `yago` |
| `global.imagePullSecrets` | Global Docker registry secret names | `[]` |
| `global.storageClass` | Global storage class | `"standard"` |

### Backend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of backend replicas | `3` |
| `backend.image.repository` | Backend image repository | `yago/backend` |
| `backend.image.tag` | Backend image tag | `v7.2` |
| `backend.image.pullPolicy` | Image pull policy | `Always` |
| `backend.service.type` | Service type | `ClusterIP` |
| `backend.service.port` | Service port | `8000` |
| `backend.resources.requests.cpu` | CPU request | `500m` |
| `backend.resources.requests.memory` | Memory request | `512Mi` |
| `backend.resources.limits.cpu` | CPU limit | `2000m` |
| `backend.resources.limits.memory` | Memory limit | `2Gi` |
| `backend.autoscaling.enabled` | Enable HPA | `true` |
| `backend.autoscaling.minReplicas` | Minimum replicas | `3` |
| `backend.autoscaling.maxReplicas` | Maximum replicas | `10` |

### Frontend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `yago/frontend` |
| `frontend.image.tag` | Frontend image tag | `v7.2` |
| `frontend.service.port` | Service port | `3000` |
| `frontend.resources.requests.cpu` | CPU request | `200m` |
| `frontend.resources.requests.memory` | Memory request | `256Mi` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts` | Ingress hosts configuration | See values.yaml |
| `ingress.tls` | TLS configuration | `[]` |

### Persistence Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable persistence | `true` |
| `persistence.data.size` | Data PVC size | `10Gi` |
| `persistence.plugins.size` | Plugins PVC size | `5Gi` |

### Secrets Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.openaiApiKey` | OpenAI API key | `""` |
| `secrets.anthropicApiKey` | Anthropic API key | `""` |
| `secrets.googleApiKey` | Google API key | `""` |
| `secrets.sessionSecret` | Session secret | `""` |
| `secrets.jwtSecret` | JWT secret | `""` |

## Examples

### Production Deployment

```yaml
# production-values.yaml
ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: yago.production.com
      paths:
        - path: /api
          pathType: Prefix
          backend: backend
        - path: /
          pathType: Prefix
          backend: frontend
  tls:
    - secretName: yago-tls-prod
      hosts:
        - yago.production.com

backend:
  replicaCount: 5
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
  autoscaling:
    minReplicas: 5
    maxReplicas: 20

frontend:
  replicaCount: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi

persistence:
  data:
    size: 100Gi
    storageClass: "fast-ssd"
  plugins:
    size: 50Gi
    storageClass: "fast-ssd"

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

Deploy:
```bash
helm install yago ./yago -f production-values.yaml --namespace yago-prod --create-namespace
```

### Development Deployment

```yaml
# dev-values.yaml
ingress:
  enabled: true
  hosts:
    - host: yago.dev.local
      paths:
        - path: /
          pathType: Prefix
          backend: frontend
        - path: /api
          pathType: Prefix
          backend: backend

backend:
  replicaCount: 1
  autoscaling:
    enabled: false
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

frontend:
  replicaCount: 1
  autoscaling:
    enabled: false
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 250m
      memory: 256Mi

persistence:
  data:
    size: 1Gi
  plugins:
    size: 1Gi
```

Deploy:
```bash
helm install yago ./yago -f dev-values.yaml --namespace yago-dev --create-namespace
```

### AWS EKS Deployment

```yaml
# aws-values.yaml
ingress:
  className: "alb"
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/xxxxx

persistence:
  data:
    storageClass: "gp3"
  plugins:
    storageClass: "gp3"

backend:
  nodeSelector:
    node.kubernetes.io/instance-type: "t3.large"

frontend:
  nodeSelector:
    node.kubernetes.io/instance-type: "t3.medium"
```

### GKE Deployment

```yaml
# gke-values.yaml
persistence:
  data:
    storageClass: "standard-rwo"
  plugins:
    storageClass: "standard-rwo"

ingress:
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "yago-ip"

backend:
  nodeSelector:
    cloud.google.com/gke-nodepool: "yago-backend-pool"
```

## Upgrading

```bash
# Get current values
helm get values yago --namespace yago > current-values.yaml

# Upgrade to new version
helm upgrade yago ./yago -f current-values.yaml --namespace yago
```

## Troubleshooting

### Check pod status
```bash
kubectl get pods -n yago
kubectl describe pod <pod-name> -n yago
kubectl logs <pod-name> -n yago
```

### Check services
```bash
kubectl get svc -n yago
kubectl describe svc yago-backend -n yago
```

### Check ingress
```bash
kubectl get ingress -n yago
kubectl describe ingress yago-ingress -n yago
```

### Check PVCs
```bash
kubectl get pvc -n yago
kubectl describe pvc yago-data-pvc -n yago
```

### Test backend health
```bash
kubectl port-forward svc/yago-backend 8000:8000 -n yago
curl http://localhost:8000/api/v1/monitoring/health
```

### Test frontend
```bash
kubectl port-forward svc/yago-frontend 3000:3000 -n yago
curl http://localhost:3000
```

## Security Considerations

1. **Secrets Management**: Use external secrets manager in production
2. **Network Policies**: Apply network policies to restrict traffic
3. **Pod Security**: Enable pod security policies/standards
4. **RBAC**: Configure proper RBAC rules
5. **Image Scanning**: Scan images for vulnerabilities
6. **TLS**: Always use TLS for production deployments

## Support

- Documentation: https://yago.dev/docs
- Issues: https://github.com/yourusername/yago/issues
- Discord: https://discord.gg/yago

## License

Apache-2.0
