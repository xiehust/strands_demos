#!/bin/bash

REGION=$1

# 1. 创建 User Pool
echo "Creating User Pool..."
POOL_RESPONSE=$(aws cognito-idp create-user-pool \
  --pool-name "ServiceAuthPool" \
  --region $REGION)
POOL_ID=$(echo $POOL_RESPONSE | jq -r '.UserPool.Id')
echo "✓ User Pool ID: $POOL_ID"

# 2. 创建 Domain
echo "Creating Domain..."
DOMAIN_PREFIX="service-auth-$(date +%s)"
aws cognito-idp create-user-pool-domain \
  --domain $DOMAIN_PREFIX \
  --user-pool-id $POOL_ID \
  --region $REGION
TOKEN_ENDPOINT="https://${DOMAIN_PREFIX}.auth.${REGION}.amazoncognito.com/oauth2/token"
DISCOVERY_URL="https://cognito-idp.${REGION}.amazonaws.com/${POOL_ID}/.well-known/openid-configuration"
echo "✓ Token URL: $TOKEN_ENDPOINT"
echo "✓ Discovery URL: $DISCOVERY_URL"

# 3. 创建 Resource Server
echo "Creating Resource Server..."
RESOURCE_SERVER_IDENTIFIER="my-api"
aws cognito-idp create-resource-server \
  --user-pool-id $POOL_ID \
  --identifier $RESOURCE_SERVER_IDENTIFIER \
  --name "My Service API" \
  --scopes \
    ScopeName=read,ScopeDescription="Read access" \
    ScopeName=write,ScopeDescription="Write access" \
  --region $REGION
echo "✓ Resource Server: $RESOURCE_SERVER_IDENTIFIER"

# 4. 创建 App Client
echo "Creating App Client..."
CLIENT_RESPONSE=$(aws cognito-idp create-user-pool-client \
  --user-pool-id $POOL_ID \
  --client-name "ServiceClient" \
  --generate-secret \
  --allowed-o-auth-flows "client_credentials" \
  --allowed-o-auth-scopes \
    "${RESOURCE_SERVER_IDENTIFIER}/read" \
    "${RESOURCE_SERVER_IDENTIFIER}/write" \
  --allowed-o-auth-flows-user-pool-client \
  --region $REGION)

CLIENT_ID=$(echo $CLIENT_RESPONSE | jq -r '.UserPoolClient.ClientId')
CLIENT_SECRET=$(echo $CLIENT_RESPONSE | jq -r '.UserPoolClient.ClientSecret')

echo "✓ Client ID: $CLIENT_ID"
echo "✓ Client Secret: $CLIENT_SECRET"

# 5. 测试获取 Token
echo -e "\nTesting token retrieval..."
TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=${RESOURCE_SERVER_IDENTIFIER}/read ${RESOURCE_SERVER_IDENTIFIER}/write")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" != "null" ]; then
  echo "✓ Token obtained successfully!"
  echo "Access Token: ${ACCESS_TOKEN:0:50}..."
else
  echo "✗ Failed to obtain token"
  echo $TOKEN_RESPONSE | jq
fi

# 输出配置摘要
OUTPUT="
================================
Service-to-Service Authentication Configuration
================================

User Pool ID: $POOL_ID
Region: $REGION
Domain Prefix: $DOMAIN_PREFIX

OAuth Discovery URL:
$DISCOVERY_URL

Token Endpoint:
$TOKEN_ENDPOINT

Resource Server: $RESOURCE_SERVER_IDENTIFIER

App Client (Service-to-Service):
  Client ID: $CLIENT_ID
  Client Secret: $CLIENT_SECRET

Scopes:
  - ${RESOURCE_SERVER_IDENTIFIER}/read
  - ${RESOURCE_SERVER_IDENTIFIER}/write

Test Token:
${ACCESS_TOKEN:0:50}...

================================
"

# Output to console
echo "$OUTPUT"

# Write to file
cat > .cognito-s2.env << EOF
POOL_ID=$POOL_ID
REGION=$REGION
DOMAIN_PREFIX=$DOMAIN_PREFIX
DISCOVERY_URL=$DISCOVERY_URL
TOKEN_ENDPOINT=$TOKEN_ENDPOINT
RESOURCE_SERVER_IDENTIFIER=$RESOURCE_SERVER_IDENTIFIER
CLIENT_ID=$CLIENT_ID
CLIENT_SECRET=$CLIENT_SECRET
SCOPES=${RESOURCE_SERVER_IDENTIFIER}/read ${RESOURCE_SERVER_IDENTIFIER}/write
ACCESS_TOKEN=$ACCESS_TOKEN
EOF

echo "✓ Configuration saved to .cognito-s2.env"

# Create a cleanup script
cat > cleanup-cognito-s2s.sh << EOF
#!/bin/bash
echo "Cleaning up Cognito S2S resources..."
aws cognito-idp delete-user-pool-domain --domain $DOMAIN_PREFIX --user-pool-id $POOL_ID --region $REGION 2>/dev/null
sleep 2
aws cognito-idp delete-user-pool --user-pool-id $POOL_ID --region $REGION 2>/dev/null
echo "✓ Resources deleted"
rm -f .cognito-s2.env cleanup-cognito-s2s.sh test-s2s-token.sh
EOF

chmod +x cleanup-cognito-s2s.sh
echo "✓ Cleanup script created: ./cleanup-cognito-s2s.sh"

# Create test script for token retrieval
cat > test-s2s-token.sh << EOF
#!/bin/bash
# Test script to retrieve S2S access token

source .cognito-s2.env

echo "Retrieving access token..."
TOKEN_RESPONSE=\$(curl -s -X POST "\$TOKEN_ENDPOINT" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -u "\${CLIENT_ID}:\${CLIENT_SECRET}" \\
  -d "grant_type=client_credentials&scope=\${SCOPES}")

ACCESS_TOKEN=\$(echo \$TOKEN_RESPONSE | jq -r '.access_token')

if [ "\$ACCESS_TOKEN" != "null" ]; then
  echo "✓ Token obtained successfully!"
  echo ""
  echo "Access Token:"
  echo \$ACCESS_TOKEN
  echo ""
  echo "Token payload:"
  echo \$ACCESS_TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
else
  echo "✗ Failed to obtain token"
  echo \$TOKEN_RESPONSE | jq
fi
EOF

chmod +x test-s2s-token.sh
echo "✓ Token test script created: ./.cognito-s2.env"

echo ""
echo "================================================"
echo "Setup complete! Use these files:"
echo "  - .cognito-s2.env: Full configuration details"
echo "  - cleanup-cognito-s2s.sh: Delete all resources"
echo "  - test-s2s-token.sh: Test token retrieval"
echo "================================================"
