#!/bin/bash

# AWS Resource Initialization Script
# Creates DynamoDB tables and S3 bucket if they don't exist

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from backend/.env (only simple key=value pairs)
load_env() {
    local ENV_FILE="${SCRIPT_DIR}/backend/.env"
    if [ -f "$ENV_FILE" ]; then
        # Only export simple variables needed for AWS setup, skip complex values like JSON arrays
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
            # Skip lines with JSON arrays or special characters that bash can't handle
            [[ "$value" =~ ^\[.*\]$ ]] && continue
            # Remove surrounding quotes if present
            value="${value%\"}"
            value="${value#\"}"
            # Export only the variables we need
            case "$key" in
                AWS_REGION|DYNAMODB_*|S3_BUCKET)
                    export "$key=$value"
                    ;;
            esac
        done < "$ENV_FILE"
    fi
}

# Get AWS Account ID
get_aws_account_id() {
    aws sts get-caller-identity --query Account --output text 2>/dev/null
}

# Check and create DynamoDB table if not exists
create_dynamodb_table_if_not_exists() {
    local TABLE_NAME=$1
    local REGION=${AWS_REGION:-us-west-2}

    echo "  Checking DynamoDB table: $TABLE_NAME..."

    # Check if table exists
    if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" > /dev/null 2>&1; then
        echo "  ✅ Table $TABLE_NAME already exists"
        return 0
    fi

    echo "  📦 Creating DynamoDB table: $TABLE_NAME..."
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --key-schema AttributeName=id,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION" > /dev/null 2>&1

    # Wait for table to be active
    echo "  ⏳ Waiting for table $TABLE_NAME to be active..."
    aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$REGION"
    echo "  ✅ Table $TABLE_NAME created successfully"
}

# Update S3_BUCKET in .env with account ID
update_s3_bucket_with_account_id() {
    local ENV_FILE="${SCRIPT_DIR}/backend/.env"
    local ACCOUNT_ID=$1

    if [ -z "$ACCOUNT_ID" ]; then
        echo "  ⚠️  Could not get AWS account ID, skipping S3 bucket update"
        return 1
    fi

    # Read current S3_BUCKET value
    local CURRENT_BUCKET=$(grep "^S3_BUCKET=" "$ENV_FILE" | cut -d'=' -f2)

    # Check if bucket already has account ID appended
    if [[ "$CURRENT_BUCKET" == *"-$ACCOUNT_ID" ]]; then
        echo "  ✅ S3_BUCKET already configured with account ID"
        return 0
    fi

    # Update S3_BUCKET with account ID
    local NEW_BUCKET="${CURRENT_BUCKET}-${ACCOUNT_ID}"
    sed -i "s|^S3_BUCKET=.*|S3_BUCKET=${NEW_BUCKET}|" "$ENV_FILE"
    echo "  ✅ S3_BUCKET updated to: $NEW_BUCKET"

    # Reload environment
    load_env
}

# Check and create S3 bucket if not exists
create_s3_bucket_if_not_exists() {
    local BUCKET_NAME=$1
    local REGION=${AWS_REGION:-us-west-2}

    if [ -z "$BUCKET_NAME" ]; then
        echo "  ⚠️  S3_BUCKET not configured, skipping bucket creation"
        return 1
    fi

    echo "  Checking S3 bucket: $BUCKET_NAME..."

    # Check if bucket exists
    if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
        echo "  ✅ Bucket $BUCKET_NAME already exists"
        return 0
    fi

    echo "  📦 Creating S3 bucket: $BUCKET_NAME..."

    # Create bucket (different command for us-east-1 vs other regions)
    if [ "$REGION" = "us-east-1" ]; then
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION" > /dev/null 2>&1
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION" > /dev/null 2>&1
    fi

    if [ $? -eq 0 ]; then
        echo "  ✅ Bucket $BUCKET_NAME created successfully"

        # Block public access (security best practice)
        echo "  🔒 Configuring bucket security..."
        aws s3api put-public-access-block \
            --bucket "$BUCKET_NAME" \
            --public-access-block-configuration \
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
            > /dev/null 2>&1

        echo "  ✅ Bucket security configured"
    else
        echo "  ❌ Failed to create bucket $BUCKET_NAME"
        return 1
    fi
}

# Main function to initialize all AWS resources
init_aws_resources() {
    echo ""
    echo "☁️  Setting up AWS resources..."

    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        echo "  ⚠️  AWS CLI not found, skipping AWS resource setup"
        echo "  💡 Install AWS CLI to enable automatic resource creation"
        return 0
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        echo "  ⚠️  AWS credentials not configured, skipping AWS resource setup"
        echo "  💡 Configure AWS credentials to enable automatic resource creation"
        return 0
    fi

    # Load environment variables
    load_env

    # Get AWS Account ID
    local ACCOUNT_ID=$(get_aws_account_id)
    echo "  📋 AWS Account ID: $ACCOUNT_ID"

    # Update S3 bucket name with account ID
    update_s3_bucket_with_account_id "$ACCOUNT_ID"

    # Create DynamoDB tables if they don't exist
    echo ""
    echo "📊 Checking DynamoDB tables..."

    if [ -n "$DYNAMODB_AGENTS_TABLE" ]; then
        create_dynamodb_table_if_not_exists "$DYNAMODB_AGENTS_TABLE"
    fi

    if [ -n "$DYNAMODB_SKILLS_TABLE" ]; then
        create_dynamodb_table_if_not_exists "$DYNAMODB_SKILLS_TABLE"
    fi

    if [ -n "$DYNAMODB_MCP_TABLE" ]; then
        create_dynamodb_table_if_not_exists "$DYNAMODB_MCP_TABLE"
    fi

    if [ -n "$DYNAMODB_SESSIONS_TABLE" ]; then
        create_dynamodb_table_if_not_exists "$DYNAMODB_SESSIONS_TABLE"
    fi

    if [ -n "$DYNAMODB_MESSAGES_TABLE" ]; then
        create_dynamodb_table_if_not_exists "$DYNAMODB_MESSAGES_TABLE"
    fi

    # Create S3 bucket if it doesn't exist
    echo ""
    echo "🪣 Checking S3 bucket..."
    create_s3_bucket_if_not_exists "$S3_BUCKET"

    echo ""
    echo "✅ AWS resources setup complete!"
}

# Run if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    init_aws_resources
fi
