#!/usr/bin/env python3
"""
AWS CDK App for Awesome Skills Platform
Deploys backend (ECS Fargate) and frontend (S3 + CloudFront) infrastructure
"""

import os
from aws_cdk import App, Environment, Tags

from stacks.backend_stack import BackendStack
from stacks.frontend_stack import FrontendStack

# Initialize CDK app
app = App()

# Get configuration from environment or context
aws_account = app.node.try_get_context("account") or os.getenv("CDK_DEFAULT_ACCOUNT")
aws_region = app.node.try_get_context("region") or os.getenv("CDK_DEFAULT_REGION", "us-east-1")
environment_name = app.node.try_get_context("environment") or "production"

env = Environment(account=aws_account, region=aws_region)

# Deploy backend infrastructure (ECR, ECS, ALB, IAM)
backend_stack = BackendStack(
    app,
    f"AwesomeSkillsPlatform-Backend-{environment_name}",
    environment_name=environment_name,
    env=env,
    description="Backend infrastructure for Awesome Skills Platform (ECS Fargate, ALB, ECR)",
)

# Deploy frontend infrastructure (S3, CloudFront)
frontend_stack = FrontendStack(
    app,
    f"AwesomeSkillsPlatform-Frontend-{environment_name}",
    environment_name=environment_name,
    backend_alb_url=backend_stack.alb_url,
    env=env,
    description="Frontend infrastructure for Awesome Skills Platform (S3, CloudFront)",
)

# Add global tags
Tags.of(app).add("Project", "Awesome Skills Platform")
Tags.of(app).add("Environment", environment_name)
Tags.of(app).add("ManagedBy", "AWS CDK")

app.synth()
