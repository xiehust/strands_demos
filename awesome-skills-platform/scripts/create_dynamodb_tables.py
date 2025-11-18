#!/usr/bin/env python3
"""
Script to create DynamoDB tables for Agent Platform.
"""
import boto3
import sys
from botocore.exceptions import ClientError

# Configuration
REGION = "us-east-1"

TABLES = [
    {
        "TableName": "agent-platform-agents",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "agent-platform-skills",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "agent-platform-mcp-servers",
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
]


def create_tables():
    """Create DynamoDB tables."""
    dynamodb = boto3.client("dynamodb", region_name=REGION)

    print(f"Creating DynamoDB tables in region: {REGION}\n")

    for table_config in TABLES:
        table_name = table_config["TableName"]
        print(f"Creating table: {table_name}...", end=" ")

        try:
            # Check if table already exists
            try:
                dynamodb.describe_table(TableName=table_name)
                print(f"⚠️  Table already exists, skipping")
                continue
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceNotFoundException":
                    raise

            # Create table
            response = dynamodb.create_table(**table_config)
            print(f"✓ Created successfully")

            # Wait for table to be active
            print(f"   Waiting for table to become active...", end=" ")
            waiter = dynamodb.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            print(f"✓ Active")

        except ClientError as e:
            print(f"✗ Error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False

    print("\n✓ All tables created successfully!")
    return True


def list_tables():
    """List existing tables."""
    dynamodb = boto3.client("dynamodb", region_name=REGION)

    print(f"\nExisting tables in {REGION}:")
    try:
        response = dynamodb.list_tables()
        tables = response.get("TableNames", [])

        if not tables:
            print("  No tables found")
        else:
            for table_name in tables:
                if table_name.startswith("agent-platform-"):
                    print(f"  ✓ {table_name}")
    except Exception as e:
        print(f"  Error listing tables: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Table Creation Script")
    print("Agent Platform")
    print("=" * 60)

    # Create tables
    success = create_tables()

    # List tables
    list_tables()

    print("\n" + "=" * 60)
    if success:
        print("Setup complete! Tables are ready to use.")
    else:
        print("Setup failed. Please check error messages above.")
        sys.exit(1)
