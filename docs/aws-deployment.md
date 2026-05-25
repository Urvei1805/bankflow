# BankFlow AWS Deployment Guide

> ⚠️ **This is optional.** The project works fully with Docker Compose locally.

## Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 1.5.0 installed
- Docker installed for image building

## Infrastructure Overview

The Terraform configuration in `infra/terraform/main.tf` provisions:

| Resource | Purpose |
|----------|---------|
| VPC | Isolated network with public/private subnets |
| ECS Fargate | Container orchestration |
| ALB | Load balancing & routing |
| RDS PostgreSQL | Managed database |
| ElastiCache Redis | Managed caching |
| ECR | Container image registry |
| S3 | Raw & processed data storage |
| CloudWatch | Centralized logging |
| IAM | Service roles & policies |

## Deployment Steps

### 1. Build & Push Docker Images
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push each service
for svc in auth-service banking-api-service analytics-service; do
  docker build -t bankflow/$svc services/$svc
  docker tag bankflow/$svc <account_id>.dkr.ecr.us-east-1.amazonaws.com/bankflow/$svc:latest
  docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/bankflow/$svc:latest
done
```

### 2. Deploy Infrastructure
```bash
cd infra/terraform
terraform init
terraform plan -var="db_password=YOUR_SECURE_PASSWORD"
terraform apply -var="db_password=YOUR_SECURE_PASSWORD"
```

### 3. Configure Secrets
Store sensitive values in AWS Secrets Manager (TODO: automate via Terraform).

### 4. Deploy Frontend
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://bankflow-frontend-us-east-1/
```

## Cost Estimation (Minimal Setup)
| Resource | Estimated Monthly Cost |
|----------|----------------------|
| ECS Fargate (3 services) | ~$30-50 |
| RDS t3.micro | ~$15 |
| ElastiCache t3.micro | ~$12 |
| ALB | ~$16 |
| S3 | ~$1 |
| **Total** | **~$75-95/month** |

## TODO
- [ ] Add NAT Gateway for private subnet egress
- [ ] Add ECS task definitions and services
- [ ] Add ALB listeners and target groups
- [ ] Add WAF rules
- [ ] Add CloudFront for frontend CDN
- [ ] Add Route53 DNS
- [ ] Add ACM SSL certificate
