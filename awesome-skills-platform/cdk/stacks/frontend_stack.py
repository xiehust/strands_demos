"""
Frontend Stack for Awesome Skills Platform
Creates: S3 bucket for static hosting, CloudFront distribution
"""

from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class FrontendStack(Stack):
    """Frontend infrastructure stack with S3 and CloudFront"""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment_name: str,
        backend_alb_url: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.environment_name = environment_name
        self.backend_alb_url = backend_alb_url

        # S3 Bucket for frontend static files
        self.frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"awesome-skills-platform-frontend-{environment_name}-{self.account}",
            removal_policy=self._get_removal_policy(),
            auto_delete_objects=(environment_name != "production"),
            public_read_access=False,  # CloudFront will access via OAI
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=(environment_name == "production"),
        )

        # Origin Access Identity for CloudFront to access S3
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self,
            "OAI",
            comment=f"OAI for Awesome Skills Platform frontend ({environment_name})",
        )

        # Grant CloudFront read access to S3
        self.frontend_bucket.grant_read(origin_access_identity)

        # CloudFront Distribution
        self.distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.frontend_bucket,
                    origin_access_identity=origin_access_identity,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                compress=True,
            ),
            # API behavior - forward to backend ALB
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=origins.HttpOrigin(
                        self.backend_alb_url,
                        protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,  # Don't cache API
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                "/ws/*": cloudfront.BehaviorOptions(
                    origin=origins.HttpOrigin(
                        self.backend_alb_url,
                        protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,  # WebSocket
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
            },
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                ),
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # Use only NA and Europe
            comment=f"Awesome Skills Platform Frontend ({environment_name})",
        )

        # Outputs
        CfnOutput(
            self,
            "FrontendBucketName",
            value=self.frontend_bucket.bucket_name,
            description="S3 bucket name for frontend",
        )

        CfnOutput(
            self,
            "FrontendURL",
            value=f"https://{self.distribution.distribution_domain_name}",
            description="CloudFront distribution URL",
        )

        CfnOutput(
            self,
            "DistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID (for cache invalidation)",
        )

    def _get_removal_policy(self):
        """Get removal policy based on environment"""
        if self.environment_name == "production":
            return RemovalPolicy.RETAIN
        return RemovalPolicy.DESTROY
