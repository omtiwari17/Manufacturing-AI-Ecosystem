# =============================================================
# eks-setup.ps1 — One-time EKS Cluster Setup
# Run this ONCE before the GitHub Actions pipeline takes over
# Prerequisites: AWS CLI, eksctl, kubectl installed
# =============================================================

$CLUSTER_NAME = "multi-agent-cluster"
$REGION = "ap-south-1"
$NODE_TYPE = "t3.medium"
$NODE_MIN = 1
$NODE_MAX = 3
$NODE_DESIRED = 2

Write-Host "=== Step 1: Verify AWS credentials ===" -ForegroundColor Cyan
aws sts get-caller-identity
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: AWS credentials not configured. Run 'aws configure' first." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Step 2: Create EKS Cluster ===" -ForegroundColor Cyan
Write-Host "This takes 15-20 minutes..." -ForegroundColor Yellow
eksctl create cluster `
    --name $CLUSTER_NAME `
    --region $REGION `
    --nodegroup-name standard-workers `
    --node-type $NODE_TYPE `
    --nodes $NODE_DESIRED `
    --nodes-min $NODE_MIN `
    --nodes-max $NODE_MAX `
    --managed

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Cluster creation failed." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Step 3: Update kubeconfig ===" -ForegroundColor Cyan
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

Write-Host "`n=== Step 4: Verify cluster nodes ===" -ForegroundColor Cyan
kubectl get nodes

Write-Host "`n=== Step 5: Deploy application ===" -ForegroundColor Cyan
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

Write-Host "`n=== Step 6: Wait for deployment ===" -ForegroundColor Cyan
kubectl rollout status deployment/unified-manufacturing-system --timeout=300s

Write-Host "`n=== Step 7: Get Load Balancer URL ===" -ForegroundColor Cyan
Write-Host "Waiting 60 seconds for LoadBalancer to provision..." -ForegroundColor Yellow
Start-Sleep -Seconds 60
kubectl get service unified-manufacturing-service

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "Copy the EXTERNAL-IP above and open it in your browser." -ForegroundColor Green
Write-Host "After this, all future deployments are handled by GitHub Actions automatically." -ForegroundColor Green