# AWS CDK Infrastructure for Awesome Skills Platform

This directory contains AWS Cloud Development Kit (CDK) infrastructure code for deploying the Awesome Skills Platform to AWS.

## ⚠️ Important Note

**Phase 9 Status**: Infrastructure-as-Code ready but **NOT deployed**.

Actual deployment requires:
1. AWS account credentials with appropriate permissions
2. AWS CDK CLI installed and bootstrapped
3. AWS costs (estimated $85-145/month - see DEPLOYMENT.md)

## Prerequisites

### Install AWS CDK

```bash
npm install -g aws-cdk

# Verify installation
cdk --version
```

### Install Python Dependencies

```bash
# From cdk/ directory
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

### Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

### Bootstrap CDK (First Time Only)

```bash
# Bootstrap your AWS account for CDK
cdk bootstrap aws://ACCOUNT-ID/REGION

# Example:
cdk bootstrap aws://123456789012/us-east-1
```

## Quick Start

### 1. Synthesize CloudFormation Template

```bash
# From cdk/ directory
cdk synth

# This generates CloudFormation templates in cdk.out/
# Review the generated templates before deploying
```

### 2. Preview Changes (Dry Run)

```bash
# See what resources will be created
cdk diff
```

### 3. Deploy Infrastructure

```bash
# Deploy both backend and frontend stacks
cdk deploy --all

# Deploy specific stack only
cdk deploy AwesomeSkillsPlatform-Backend-production
cdk deploy AwesomeSkillsPlatform-Frontend-production

# Auto-approve (skip confirmation)
cdk deploy --all --require-approval never
```

### 4. View Outputs

After deployment, CDK will output important values:
- **LoadBalancerURL**: Backend API endpoint
- **ECRRepositoryURI**: Docker registry for backend images
- **FrontendURL**: CloudFront URL for frontend
- **DistributionId**: CloudFront distribution ID

## What This Creates

### Backend Stack
- **VPC**: 2 AZs with public/private subnets, 1 NAT gateway
- **ECR Repository**: Docker image registry
- **ECS Fargate Cluster**: Serverless container orchestration
- **ECS Service**: 2 tasks (auto-scaling 2-10 based on CPU)
- **Application Load Balancer**: Public-facing HTTP endpoint
- **IAM Roles**: Least-privilege access for DynamoDB, Bedrock, AgentCore
- **CloudWatch Log Group**: Application logs with 1-week retention

### Frontend Stack
- **S3 Bucket**: Static website hosting
- **CloudFront Distribution**: Global CDN with HTTPS
- **Origin Access Identity**: Secure S3 access
- **Cache Behaviors**:
  - `/api/*` → Backend ALB (no cache)
  - `/ws/*` → WebSocket support (no cache)
  - `/*` → S3 static files (optimized cache)

## Customization

### Environment Configuration

```bash
# Deploy to different environment
cdk deploy --all --context environment=staging

# Specify AWS account and region
cdk deploy --all \
  --context account=123456789012 \
  --context region=us-west-2
```

### Task CPU/Memory

Edit `cdk/stacks/backend_stack.py`:

```python
task_definition = ecs.FargateTaskDefinition(
    self,
    "TaskDefinition",
    memory_limit_mib=2048,  # Change from 1024 to 2048 (2 GB)
    cpu=1024,               # Change from 512 to 1024 (1 vCPU)
    ...
)
```

### Auto-Scaling Thresholds

Edit `cdk/stacks/backend_stack.py`:

```python
scaling.scale_on_cpu_utilization(
    "CpuScaling",
    target_utilization_percent=70,  # Adjust threshold
    scale_in_cooldown=Duration.seconds(60),
    scale_out_cooldown=Duration.seconds(60),
)
```

### CloudFront Price Class

Edit `cdk/stacks/frontend_stack.py`:

```python
self.distribution = cloudfront.Distribution(
    ...
    price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,  # Global
    # or PRICE_CLASS_100 (NA + Europe only)
)
```

## Deployment Workflow

### Initial Deployment

```bash
# 1. Build and push Docker image
cd /path/to/project
docker build -t awesome-skills-platform-backend:latest .

# 2. Get ECR login and repository URI from CDK output
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# 3. Tag and push
docker tag awesome-skills-platform-backend:latest \
    123456789012.dkr.ecr.us-east-1.amazonaws.com/awesome-skills-platform-backend-production:latest

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/awesome-skills-platform-backend-production:latest

# 4. Build frontend
cd frontend/
npm install
npm run build

# 5. Upload to S3 (use bucket name from CDK output)
aws s3 sync dist/ s3://awesome-skills-platform-frontend-production-123456789012/ \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --exclude "index.html"

aws s3 cp dist/index.html s3://awesome-skills-platform-frontend-production-123456789012/ \
    --cache-control "public, max-age=0, must-revalidate"

# 6. Invalidate CloudFront cache (use distribution ID from CDK output)
aws cloudfront create-invalidation \
    --distribution-id E1234567890ABC \
    --paths "/*"
```

### Update Deployment

```bash
# 1. Update infrastructure
cdk deploy --all

# 2. Push new Docker image (ECS will auto-deploy)
docker build -t awesome-skills-platform-backend:latest .
docker tag awesome-skills-platform-backend:latest ECR_URI:latest
docker push ECR_URI:latest

# Force ECS service update
aws ecs update-service \
    --cluster awesome-skills-platform-production \
    --service SERVICE_NAME \
    --force-new-deployment

# 3. Update frontend
cd frontend/ && npm run build
aws s3 sync dist/ s3://BUCKET_NAME/ --delete
aws cloudfront create-invalidation --distribution-id DIST_ID --paths "/*"
```

## Stack Dependencies

```
BackendStack → FrontendStack
   │               │
   ├─ VPC          └─ S3 Bucket
   ├─ ECR              └─ CloudFront (uses ALB URL from BackendStack)
   ├─ ECS
   └─ ALB
```

Frontend stack depends on Backend stack's ALB URL for API routing.

## Monitoring

### View ECS Logs

```bash
# Tail logs in real-time
aws logs tail /ecs/awesome-skills-platform-backend-production --follow

# Query specific errors
aws logs filter-pattern '{ $.level = "ERROR" }' \
    --log-group-name /ecs/awesome-skills-platform-backend-production \
    --start-time $(date -u -d '1 hour ago' +%s)000
```

### CloudWatch Dashboard

Create custom dashboard at: https://console.aws.amazon.com/cloudwatch/

Recommended metrics:
- ECS service CPU/Memory utilization
- ALB request count, latency, 4xx/5xx
- Target group healthy host count
- CloudFront requests, error rate

## Cost Management

### Set Up Billing Alerts

```bash
# Create budget (one-time setup)
aws budgets create-budget --account-id YOUR_ACCOUNT_ID \
    --budget file://budget.json
```

Example `budget.json`:
```json
{
  "BudgetName": "AwesomeSkillsPlatformBudget",
  "BudgetLimit": {
    "Amount": "150",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

## Cleanup

### Destroy All Resources

```bash
# ⚠️ WARNING: This will delete all infrastructure
cdk destroy --all

# Destroy specific stack
cdk destroy AwesomeSkillsPlatform-Frontend-production
cdk destroy AwesomeSkillsPlatform-Backend-production

# Auto-approve (skip confirmation)
cdk destroy --all --force
```

**Note**: Some resources (ECR images, S3 objects) may need manual cleanup depending on removal policy.

## Troubleshooting

### CDK Bootstrap Error

```bash
# Re-bootstrap your account
cdk bootstrap aws://ACCOUNT-ID/REGION --force
```

### ECR Push Permission Denied

```bash
# Refresh ECR login
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

### ECS Tasks Failing to Start

1. Check CloudWatch logs
2. Verify IAM role permissions
3. Ensure ECR image exists and is accessible
4. Check task definition environment variables

### CloudFront Not Serving Latest Frontend

```bash
# Invalidate cache
aws cloudfront create-invalidation \
    --distribution-id DIST_ID \
    --paths "/*"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to AWS
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

      - name: Deploy CDK
        run: |
          cd cdk
          pip install -r requirements.txt
          cdk deploy --all --require-approval never
```

## Additional Resources

- **AWS CDK Documentation**: https://docs.aws.amazon.com/cdk/
- **CDK Python Reference**: https://docs.aws.amazon.com/cdk/api/v2/python/
- **Platform Documentation**: [../DEPLOYMENT.md](../DEPLOYMENT.md)
- **Architecture Details**: [../ARCHITECTURE.md](../ARCHITECTURE.md)

## Support

For issues with:
- **CDK Syntax**: See [CDK Python API Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- **AWS Services**: Check AWS Console and CloudWatch logs
- **Application**: See [../README.md](../README.md) and [../CLAUDE.md](../CLAUDE.md)
