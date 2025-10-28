# YAGO Deployment Guide

Complete guide for deploying YAGO in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Providers](#cloud-providers)
6. [Production Checklist](#production-checklist)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Docker**: 20.10+ ([Install](https://docs.docker.com/get-docker/))
- **Kubernetes**: 1.19+ ([Install](https://kubernetes.io/docs/tasks/tools/))
- **kubectl**: Latest ([Install](https://kubernetes.io/docs/tasks/tools/install-kubectl/))
- **Helm**: 3.0+ ([Install](https://helm.sh/docs/intro/install/))

### Optional Tools

- **k9s**: Kubernetes CLI UI ([Install](https://k9scli.io/))
- **kubectx**: Kubernetes context switcher ([Install](https://github.com/ahmetb/kubectx))
- **stern**: Multi-pod log tailing ([Install](https://github.com/stern/stern))

---

## Quick Start

### One-Command Kubernetes Deployment

```bash
# Deploy to Kubernetes with Helm
./deployment/scripts/deploy.sh --environment production

# Or with custom values
./deployment/scripts/deploy.sh -f my-values.yaml
```

### One-Command Docker Deployment

```bash
# Deploy with Docker Compose
cd deployment/docker
docker-compose -f docker-compose.prod.yml up -d
```

---

## Kubernetes Deployment

### Method 1: Using Helm (Recommended)

#### 1. Install with Default Values

```bash
helm install yago ./deployment/kubernetes/helm/yago \
  --namespace yago \
  --create-namespace
```

#### 2. Install with Custom Values

Create `my-values.yaml`:

```yaml
ingress:
  enabled: true
  hosts:
    - host: yago.yourdomain.com
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
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi

frontend:
  replicaCount: 3
```

Deploy:

```bash
helm install yago ./deployment/kubernetes/helm/yago \
  -f my-values.yaml \
  --namespace yago \
  --create-namespace
```

#### 3. Upgrade Existing Deployment

```bash
helm upgrade yago ./deployment/kubernetes/helm/yago \
  -f my-values.yaml \
  --namespace yago
```

#### 4. Rollback if Needed

```bash
# List releases
helm history yago --namespace yago

# Rollback to previous
helm rollback yago --namespace yago

# Rollback to specific revision
helm rollback yago 3 --namespace yago
```

### Method 2: Using kubectl (Advanced)

#### 1. Apply Manifests

```bash
# Create namespace
kubectl apply -f deployment/kubernetes/manifests/namespace.yaml

# Apply configurations
kubectl apply -f deployment/kubernetes/manifests/configmap.yaml
kubectl apply -f deployment/kubernetes/manifests/secrets.yaml

# Apply storage
kubectl apply -f deployment/kubernetes/manifests/persistent-volume.yaml

# Deploy backend
kubectl apply -f deployment/kubernetes/manifests/backend-deployment.yaml
kubectl apply -f deployment/kubernetes/manifests/backend-service.yaml

# Deploy frontend
kubectl apply -f deployment/kubernetes/manifests/frontend-deployment.yaml
kubectl apply -f deployment/kubernetes/manifests/frontend-service.yaml

# Apply ingress
kubectl apply -f deployment/kubernetes/manifests/ingress.yaml

# Apply autoscaling
kubectl apply -f deployment/kubernetes/manifests/hpa.yaml
```

#### 2. Verify Deployment

```bash
# Check pods
kubectl get pods -n yago

# Check services
kubectl get svc -n yago

# Check ingress
kubectl get ingress -n yago

# Watch deployment
kubectl get pods -n yago -w
```

### Method 3: Using Deployment Script

```bash
# Production deployment
./deployment/scripts/deploy.sh \
  --environment production \
  --namespace yago-prod \
  --release yago-prod

# Staging deployment
./deployment/scripts/deploy.sh \
  --environment staging \
  --namespace yago-staging \
  --release yago-staging

# Development deployment
./deployment/scripts/deploy.sh \
  --environment development \
  --namespace yago-dev \
  --release yago-dev
```

---

## Docker Deployment

### Development Environment

```bash
docker-compose up -d
```

### Production Environment

```bash
# Create .env file with secrets
cat > .env <<EOF
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-key
SESSION_SECRET=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
EOF

# Deploy
cd deployment/docker
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml yago

# Check services
docker stack services yago

# View logs
docker service logs yago_backend
```

---

## Cloud Providers

### AWS EKS

#### 1. Create EKS Cluster

```bash
# Using eksctl
eksctl create cluster \
  --name yago-cluster \
  --region us-east-1 \
  --node-type t3.large \
  --nodes 3

# Configure kubectl
aws eks update-kubeconfig --name yago-cluster --region us-east-1
```

#### 2. Install AWS Load Balancer Controller

```bash
# Add EKS Helm repo
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Install controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=yago-cluster
```

#### 3. Deploy YAGO

```yaml
# aws-values.yaml
ingress:
  className: "alb"
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:...

persistence:
  data:
    storageClass: "gp3"
  plugins:
    storageClass: "gp3"
```

```bash
helm install yago ./deployment/kubernetes/helm/yago \
  -f aws-values.yaml \
  --namespace yago \
  --create-namespace
```

### Google GKE

#### 1. Create GKE Cluster

```bash
# Create cluster
gcloud container clusters create yago-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Get credentials
gcloud container clusters get-credentials yago-cluster \
  --zone us-central1-a
```

#### 2. Deploy YAGO

```yaml
# gke-values.yaml
ingress:
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "yago-ip"

persistence:
  data:
    storageClass: "standard-rwo"
  plugins:
    storageClass: "standard-rwo"
```

```bash
helm install yago ./deployment/kubernetes/helm/yago \
  -f gke-values.yaml \
  --namespace yago \
  --create-namespace
```

### Azure AKS

#### 1. Create AKS Cluster

```bash
# Create resource group
az group create --name yago-rg --location eastus

# Create cluster
az aks create \
  --resource-group yago-rg \
  --name yago-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials \
  --resource-group yago-rg \
  --name yago-cluster
```

#### 2. Deploy YAGO

```yaml
# aks-values.yaml
ingress:
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway

persistence:
  data:
    storageClass: "managed-premium"
  plugins:
    storageClass: "managed-premium"
```

```bash
helm install yago ./deployment/kubernetes/helm/yago \
  -f aks-values.yaml \
  --namespace yago \
  --create-namespace
```

---

## Production Checklist

### Before Deployment

- [ ] Update all API keys and secrets
- [ ] Configure TLS certificates
- [ ] Set up DNS records
- [ ] Configure monitoring and alerting
- [ ] Set up backup strategy
- [ ] Review resource limits
- [ ] Configure auto-scaling
- [ ] Set up logging aggregation
- [ ] Review security policies
- [ ] Test disaster recovery plan

### Security

- [ ] Use external secrets manager (AWS Secrets Manager, Vault, etc.)
- [ ] Enable network policies
- [ ] Configure pod security policies
- [ ] Enable RBAC
- [ ] Use non-root containers
- [ ] Scan images for vulnerabilities
- [ ] Enable audit logging
- [ ] Configure firewall rules
- [ ] Set up VPN access
- [ ] Enable encryption at rest

### Monitoring

- [ ] Configure Prometheus scraping
- [ ] Set up Grafana dashboards
- [ ] Configure alerting rules
- [ ] Set up log aggregation (ELK, Loki, etc.)
- [ ] Configure uptime monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure APM (Application Performance Monitoring)

### Backup

- [ ] Configure database backups
- [ ] Set up persistent volume backups
- [ ] Test restore procedures
- [ ] Document backup schedules
- [ ] Configure off-site backups

---

## Monitoring & Maintenance

### Health Checks

```bash
# Check backend health
kubectl port-forward -n yago svc/yago-backend 8000:8000
curl http://localhost:8000/api/v1/monitoring/health

# Check metrics
curl http://localhost:8000/api/v1/monitoring/metrics
```

### Logs

```bash
# View backend logs
kubectl logs -f deployment/yago-backend -n yago

# View all logs
kubectl logs -f -l app=yago -n yago

# Using stern
stern yago -n yago
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment yago-backend --replicas=10 -n yago

# Check HPA status
kubectl get hpa -n yago

# Describe HPA
kubectl describe hpa yago-backend-hpa -n yago
```

### Updates

```bash
# Rolling update
kubectl set image deployment/yago-backend \
  backend=yago/backend:v7.3 \
  -n yago

# Check rollout status
kubectl rollout status deployment/yago-backend -n yago

# Rollback if needed
kubectl rollout undo deployment/yago-backend -n yago
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n yago

# Check events
kubectl get events -n yago --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n yago --previous
```

### Connection Issues

```bash
# Test connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside pod:
wget -O- http://yago-backend:8000/api/v1/monitoring/health
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n yago

# Describe PVC
kubectl describe pvc yago-data-pvc -n yago

# Check storage class
kubectl get storageclass
```

### Performance Issues

```bash
# Check resource usage
kubectl top pods -n yago
kubectl top nodes

# Check HPA metrics
kubectl get hpa -n yago -w
```

### Common Issues

#### Issue: ImagePullBackOff

**Solution**: Check image name and credentials

```bash
kubectl describe pod <pod-name> -n yago
# Check imagePullSecrets if using private registry
```

#### Issue: CrashLoopBackOff

**Solution**: Check application logs and configuration

```bash
kubectl logs <pod-name> -n yago --previous
kubectl describe pod <pod-name> -n yago
```

#### Issue: Pending Pods

**Solution**: Check resource availability

```bash
kubectl describe pod <pod-name> -n yago
# Look for resource constraints or node selector issues
```

---

## Support

- **Documentation**: https://yago.dev/docs
- **GitHub Issues**: https://github.com/yourusername/yago/issues
- **Discord**: https://discord.gg/yago
- **Email**: team@yago.dev

---

## License

Apache-2.0
