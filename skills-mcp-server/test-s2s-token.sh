#!/bin/bash
# Test script to retrieve S2S access token

source .cognito-s2.env

echo "Retrieving access token..."
TOKEN_RESPONSE=$(curl -s -X POST "$TOKEN_ENDPOINT" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=${SCOPES}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" != "null" ]; then
  echo "✓ Token obtained successfully!"
  echo ""
  echo "Access Token:"
  echo $ACCESS_TOKEN
  echo ""
  echo "Token payload:"
  echo $ACCESS_TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
else
  echo "✗ Failed to obtain token"
  echo $TOKEN_RESPONSE | jq
fi
