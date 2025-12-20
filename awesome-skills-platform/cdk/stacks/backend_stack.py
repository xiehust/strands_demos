"""
Backend Stack for Awesome Skills Platform
Creates: VPC, ECR, ECS Fargate, ALB, IAM roles, CloudWatch logs
"""

from aws_cdk import (
    Stack,
    CfnOutput,
    Duration,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct


class BackendStack(Stack):
    """Backend infrastructure stack with ECS Fargate and ALB"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.environment_name = environment_name

        # VPC - Create new VPC with public/private subnets
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=2,  # Use 2 availability zones for high availability
            nat_gateways=1,  # Use 1 NAT gateway to save costs
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        # ECR Repository for backend Docker images
        self.ecr_repository = ecr.Repository(
            self,
            "BackendRepository",
            repository_name=f"awesome-skills-platform-backend-{environment_name}",
            removal_policy=self._get_removal_policy(),
            image_scan_on_push=True,  # Enable vulnerability scanning
        )

        # ECS Cluster
        self.cluster = ecs.Cluster(
            self,
            "Cluster",
            cluster_name=f"awesome-skills-platform-{environment_name}",
            vpc=self.vpc,
            container_insights=True,  # Enable CloudWatch Container Insights
        )

        # Task Execution Role (for pulling images, logs)
        task_execution_role = iam.Role(
            self,
            "TaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
        )

        # Task Role (for application permissions: DynamoDB, Bedrock, etc.)
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # Grant DynamoDB permissions
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                resources=[
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/awesome-skills-platform-*"
                ],
            )
        )

        # Grant Bedrock permissions
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        # Grant AgentCore Memory permissions
        task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock-agentcore:*",
                ],
                resources=["*"],
            )
        )

        # CloudWatch Log Group
        log_group = logs.LogGroup(
            self,
            "BackendLogGroup",
            log_group_name=f"/ecs/awesome-skills-platform-backend-{environment_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=self._get_removal_policy(),
        )

        # Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDefinition",
            memory_limit_mib=1024,  # 1 GB
            cpu=512,  # 0.5 vCPU
            execution_role=task_execution_role,
            task_role=task_role,
        )

        # Container Definition
        container = task_definition.add_container(
            "BackendContainer",
            image=ecs.ContainerImage.from_ecr_repository(
                self.ecr_repository, tag="latest"
            ),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="backend", log_group=log_group
            ),
            environment={
                "AWS_REGION": self.region,
                "DYNAMODB_TABLE_PREFIX": "awesome-skills-platform",
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": environment_name,
            },
            health_check=ecs.HealthCheck(
                command=["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                retries=3,
                start_period=Duration.seconds(60),
            ),
        )

        container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # Application Load Balanced Fargate Service
        self.service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=self.cluster,
            task_definition=task_definition,
            desired_count=2,  # Run 2 tasks for high availability
            public_load_balancer=True,
            listener_port=80,
            target_protocol=elbv2.ApplicationProtocol.HTTP,
            health_check_grace_period=Duration.seconds(60),
        )

        # Configure target group health check
        self.service.target_group.configure_health_check(
            path="/health",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3,
        )

        # Configure auto-scaling based on CPU
        scaling = self.service.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=10,
        )

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        # Store ALB URL for frontend stack
        self.alb_url = self.service.load_balancer.load_balancer_dns_name

        # Outputs
        CfnOutput(
            self,
            "LoadBalancerURL",
            value=f"http://{self.alb_url}",
            description="Backend API URL",
        )

        CfnOutput(
            self,
            "ECRRepositoryURI",
            value=self.ecr_repository.repository_uri,
            description="ECR repository URI for backend images",
        )

        CfnOutput(
            self,
            "ECSClusterName",
            value=self.cluster.cluster_name,
            description="ECS cluster name",
        )

        CfnOutput(
            self,
            "ECSServiceName",
            value=self.service.service.service_name,
            description="ECS service name",
        )

    def _get_removal_policy(self):
        """Get removal policy based on environment"""
        from aws_cdk import RemovalPolicy

        if self.environment_name == "production":
            return RemovalPolicy.RETAIN
        return RemovalPolicy.DESTROY
