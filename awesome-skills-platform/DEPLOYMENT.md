# Deployment Guide - Awesome Skills Platform

**Version**: 2.0
**Last Updated**: 2025-11-18
**Status**: Infrastructure-as-Code Ready (AWS CDK)

## Overview

This guide provides comprehensive instructions for deploying the Awesome Skills Platform to AWS production environment. The platform is fully functional locally and ready for cloud deployment.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Load Balancer               │
│                                                             │
│  /api/*     → ECS Fargate (Backend API + Agent Runtime)    │
│  /*         → S3 Static Website (React Frontend)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │                                      │
┌───────▼────────┐              ┌──────────────▼──────┐
│   ECS Fargate  │              │  S3 Static Hosting  │
│                │              │                     │
│  - Backend API │              │  - React Frontend   │
│  - Uvicorn     │              │  - index.html       │
│  - Python 3.12 │              │  - Static assets    │
└────────┬───────┘              └─────────────────────┘
         │
    ┌────▼────────────────────────────────────────┐
    │                                             │
    │  ┌─────────────┐  ┌────────────────────┐   │
    │  │  DynamoDB   │  │  AWS Bedrock       │   │
    │  │  (Metadata) │  │  (Claude Models)   │   │
    │  └─────────────┘  └────────────────────┘   │
    │                                             │
    │  ┌─────────────┐  ┌────────────────────┐   │
    │  │ AgentCore   │  │   CloudWatch       │   │
    │  │  Memory     │  │  (Monitoring)      │   │
    │  └─────────────┘  └────────────────────┘   │
    └─────────────────────────────────────────────┘
```

## 📋 Prerequisites

### AWS Account Setup
1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured (`aws configure`)
3. **AWS CDK CLI** installed (`npm install -g aws-cdk`)
4. **Docker** for building images
5. **Node.js** >= 18 for frontend build and CDK

### Required AWS Services
- ✅ Amazon ECS (Elastic Container Service)
- ✅ Amazon ECR (Elastic Container Registry)
- ✅ Application Load Balancer
- ✅ Amazon S3
- ✅ Amazon DynamoDB (already configured)
- ✅ AWS Bedrock (already configured)
- ✅ AgentCore Memory (optional)
- ✅ Amazon CloudWatch
- ✅ AWS Secrets Manager

### IAM Permissions Required
- ECS: Full access
- ECR: Full access
- S3: Full access
- ALB: Full access
- DynamoDB: Read/Write
- Bedrock: Invoke model
- CloudWatch: Write logs and metrics
- Secrets Manager: Read secrets

## 🚀 Deployment Steps

### Step 1: Environment Configuration

Create `.env.production` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id

# Application Configuration
APP_NAME=awesome-skills-platform
ENVIRONMENT=production

# DynamoDB (already exists)
DYNAMODB_TABLE_PREFIX=awesome-skills-platform

# AgentCore Memory (optional - enable if you have memory_id)
AGENTCORE_MEMORY_ID=your-memory-id

# Bedrock Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Backend Configuration
BACKEND_PORT=8000
LOG_LEVEL=INFO

# Frontend Configuration
VITE_API_URL=https://your-domain.com/api
```

### Step 2: Build and Push Backend Docker Image

```bash
# Build Docker image
docker build -t awesome-skills-platform-backend:latest .

# Tag for ECR
docker tag awesome-skills-platform-backend:latest \\
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/awesome-skills-platform-backend:latest

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \\
    docker login --username AWS --password-stdin \\
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Push image
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/awesome-skills-platform-backend:latest
```

### Step 3: Build and Deploy Frontend to S3

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm install

# Build for production
npm run build

# Upload to S3
aws s3 sync dist/ s3://awesome-skills-platform-frontend/ \\
    --delete \\
    --cache-control "public, max-age=31536000, immutable" \\
    --exclude "index.html"

# Upload index.html with different cache settings
aws s3 cp dist/index.html s3://awesome-skills-platform-frontend/ \\
    --cache-control "public, max-age=0, must-revalidate"

# Enable static website hosting
aws s3 website s3://awesome-skills-platform-frontend/ \\
    --index-document index.html \\
    --error-document index.html
```

### Step 4: Deploy Infrastructure with AWS CDK

```bash
# Navigate to CDK directory
cd cdk/

# Install CDK dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1

# Synthesize CloudFormation templates (review)
cdk synth

# Preview changes
cdk diff

# Deploy all stacks
cdk deploy --all

# Note the outputs: LoadBalancerURL, ECRRepositoryURI, FrontendURL, DistributionId
```

### Step 5: Verify Infrastructure

CDK automatically configures:

**Application Load Balancer:**
- Health check path: `/health`
- Port: 8000
- Protocol: HTTP
- Auto-configured target group

**CloudFront Distribution:**
- `/api/*` → Backend ALB (no cache)
- `/ws/*` → WebSocket support (no cache)
- `/*` → S3 static files (optimized cache)
- HTTPS enforced with HTTP → HTTPS redirect

### Step 6: Configure CloudWatch Monitoring

**Log Groups (automatically created by CDK):**
- `/ecs/awesome-skills-platform-backend-production` - Backend application logs
- Container Insights enabled for ECS cluster metrics

**Dashboards to Create:**
1. **API Performance**
   - Request count
   - Response time (P50, P90, P99)
   - Error rate
   - 4xx/5xx counts

2. **Agent Metrics**
   - Active conversations
   - Bedrock API calls
   - Skill invocations
   - MCP tool usage

3. **Infrastructure**
   - ECS task count
   - CPU utilization
   - Memory utilization
   - DynamoDB read/write capacity

**Alarms to Configure:**
- Error rate > 5% (5 minutes)
- P99 latency > 10 seconds
- ECS task count < 2
- DynamoDB throttling events

### Step 7: Configure Environment Variables (Optional)

For sensitive configuration, you can:

**Option 1: Use ECS Task Definition environment variables** (edit `cdk/stacks/backend_stack.py`):
```python
environment={
    "AWS_REGION": self.region,
    "DYNAMODB_TABLE_PREFIX": "awesome-skills-platform",
    "AGENTCORE_MEMORY_ID": "your-memory-id",  # Add here
    "LOG_LEVEL": "INFO",
}
```

**Option 2: Use AWS Secrets Manager**:
```bash
# Create secret for environment variables
aws secretsmanager create-secret \
    --name awesome-skills-platform/env \
    --description "Environment variables for Awesome Skills Platform" \
    --secret-string file://secrets.json

# Then modify backend_stack.py to add secrets reference
```

## 🔒 Security Checklist

### Pre-Deployment
- [ ] Review IAM roles and policies (least privilege)
- [ ] Enable VPC flow logs
- [ ] Configure Security Groups (restrict to necessary ports)
- [ ] Enable S3 bucket encryption
- [ ] Enable CloudWatch log encryption
- [ ] Configure WAF rules (optional but recommended)

### Post-Deployment
- [ ] Verify SSL/TLS certificates
- [ ] Test CORS configuration
- [ ] Review CloudWatch alarms
- [ ] Test backup and recovery procedures
- [ ] Conduct security audit
- [ ] Enable AWS GuardDuty (threat detection)

## 📊 Monitoring and Maintenance

### Daily Monitoring
- Check CloudWatch dashboards
- Review error logs in CloudWatch Logs Insights
- Monitor Bedrock API usage and costs
- Check DynamoDB capacity metrics

### Weekly Maintenance
- Review and rotate logs
- Check ECS task health
- Review S3 storage costs
- Update dependencies (security patches)

### Monthly Tasks
- Cost optimization review
- Performance tuning
- Capacity planning
- Security audit

## 🔧 Troubleshooting

### Backend Not Starting

**Check ECS logs:**
```bash
aws logs tail /ecs/awesome-skills-platform-backend --follow
```

**Common issues:**
- Missing environment variables (check Secrets Manager)
- IAM permissions for Bedrock/DynamoDB
- Network connectivity to DynamoDB

### Frontend Not Loading

**Check S3 bucket policy:**
```bash
aws s3api get-bucket-policy --bucket awesome-skills-platform-frontend
```

**Common issues:**
- Missing index.html
- Incorrect CORS configuration
- CloudFront cache not invalidated

### High Error Rate

**Query recent errors:**
```bash
aws logs filter-pattern '{ $.level = "ERROR" }' \\
    --log-group-name /ecs/awesome-skills-platform-backend \\
    --start-time $(date -u -d '1 hour ago' +%s)000
```

## 💰 Cost Estimation

**Monthly AWS Costs (estimated):**

| Service | Configuration | Est. Cost/Month |
|---------|--------------|-----------------|
| ECS Fargate | 2 tasks × 0.5 vCPU, 1GB RAM | ~$30 |
| Application Load Balancer | Standard ALB | ~$23 |
| S3 Static Hosting | 1GB storage, 10GB transfer | ~$2 |
| DynamoDB | On-demand, moderate usage | ~$10-50 |
| AWS Bedrock | Claude Sonnet 4.5, variable | Variable* |
| CloudWatch | Logs + Metrics | ~$10 |
| Data Transfer | Outbound data | ~$10-30 |
| **Total** | | **~$85-145/month** |

*Bedrock costs depend on usage: ~$3 per million input tokens, ~$15 per million output tokens

## 🔄 CI/CD Pipeline (Optional)

Use GitHub Actions for automated CDK deployments:

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Install CDK
        run: npm install -g aws-cdk

      - name: Deploy infrastructure
        run: |
          cd cdk
          pip install -r requirements.txt
          cdk deploy --all --require-approval never

      - name: Build and push Docker image
        run: |
          docker build -t backend .
          docker tag backend:latest $ECR_URI:latest
          docker push $ECR_URI:latest

      - name: Build and deploy frontend
        run: |
          cd frontend && npm run build
          aws s3 sync dist/ s3://$S3_BUCKET/ --delete
          aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"

      - name: Force ECS service update
        run: |
          aws ecs update-service \
            --cluster awesome-skills-platform-production \
            --service $SERVICE_NAME \
            --force-new-deployment
```

## 📞 Support and Resources

- **Platform Documentation**: [README.md](./README.md)
- **Architecture Details**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Development Plan**: [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)
- **CDK Documentation**: [cdk/README.md](./cdk/README.md)
- **API Documentation**: http://localhost:8000/docs (when running locally)

## ⚠️ Important Notes

1. **Cost Awareness**: Monitor AWS costs carefully, especially Bedrock API usage
2. **Security**: Never commit secrets to version control
3. **Backup**: Implement DynamoDB backup strategy
4. **Scaling**: Configure ECS Auto Scaling based on CPU/Memory
5. **Disaster Recovery**: Test backup restoration procedures

## 🎉 Production Checklist

Before going live:

- [ ] CDK bootstrapped: `cdk bootstrap`
- [ ] Infrastructure deployed: `cdk deploy --all`
- [ ] Backend Docker image pushed to ECR
- [ ] ECS tasks running and healthy
- [ ] Frontend built and uploaded to S3
- [ ] CloudFront distribution active
- [ ] Backend health check passing (via ALB)
- [ ] Frontend accessible via CloudFront URL
- [ ] DynamoDB tables created and accessible
- [ ] Bedrock API connectivity verified
- [ ] CloudWatch Container Insights enabled
- [ ] Alarms configured (optional)
- [ ] SSL/TLS certificates installed (optional - use ACM)
- [ ] Domain name configured (optional - Route 53 + CloudFront)
- [ ] Backup strategy implemented (DynamoDB on-demand backups)
- [ ] Security audit completed
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Team trained on CDK operations

---

**Ready to Deploy?** The platform is production-ready with AWS CDK. Review this guide and `cdk/README.md` carefully before deployment.
