#!/bin/bash
echo "Cleaning up Cognito S2S resources..."
aws cognito-idp delete-user-pool-domain --domain service-auth-1763002023 --user-pool-id us-east-1_MTVrzbBMX --region us-east-1 2>/dev/null
sleep 2
aws cognito-idp delete-user-pool --user-pool-id us-east-1_MTVrzbBMX --region us-east-1 2>/dev/null
echo "✓ Resources deleted"
rm -f .cognito-s2.env cleanup-cognito-s2s.sh test-s2s-token.sh
