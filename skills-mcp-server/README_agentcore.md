## Setup Congito
- Run below scripts to setup a cognito user pool for MCP runtime
```bash
./setup_cognito_s2s.sh us-east-1
```
运行之后，会生成一个`.cognito-s2.env`文件，里面的信息在下面configure中会用到

## configure 
```bash
agentcore configure -e src/server_agentcore.py -r us-east-1 --protocol MCP
```
⚠️注意：Select deployment type: 2. Container

## Edit Docker file
运行configure之后，在.bedrock_agentcore/skills_mcp/下生成一个Dockerfile，在第3行后，加入nodejs依赖
```Dockerfile
# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs zip \
    && rm -rf /var/lib/apt/lists/*
```

## launch
```bash
agentcore launch
```

## Create S3 Bucket
从`.bedrock_agentcore.yaml`找到生成的 execution_role，添加s3权限

```bash
# 1. Create bucket
aws s3 mb s3://skills-mcp-server-{region}-{account_id} --region {regino}

# 2. Add read/write policy to role
aws iam put-role-policy \
    --role-name ${execution_role} \
    --policy-name S3ReadWritePolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::skills-mcp-server-${region}-${account_id}",
                    "arn:aws:s3:::skills-mcp-server-${region}-${account_id}/*"
                ]
            }
        ]
    }'
```


## test
替换`test_agentcore_mcp.py` runtime_arn为部署好的arn，运行 `python test_agentcore_mcp.py`