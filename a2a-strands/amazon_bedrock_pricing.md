# Amazon Bedrock Pricing Model

Amazon Bedrock follows a pay-as-you-go pricing model with two main pricing components:

## 1. Pay-Per-Use Model
- You are charged based on the actual usage of foundation models
- Pricing is calculated based on two factors:
  - Number of input tokens processed
  - Number of output tokens generated
- You only pay for the services you actually use
- Different models have different pricing rates

## 2. Provisioned Throughput Option
For users requiring guaranteed capacity or using custom models, Amazon Bedrock offers Provisioned Throughput with the following characteristics:

- **Billing**: Hourly billing for reserved capacity
- **Model Units (MUs)**: Capacity is measured in Model Units that specify:
  - Number of input tokens that can be processed per minute
  - Number of output tokens that can be generated per minute

### Provisioned Throughput Commitment Options:
1. **No commitment**: Can be deleted at any time
2. **1-month commitment**: Must maintain for one month
3. **6-month commitment**: Must maintain for six months
- Longer commitments offer more discounted hourly rates

### Pricing Factors for Provisioned Throughput:
1. The specific model chosen
2. Number of Model Units (MUs) purchased
3. Duration of commitment

## Important Notes:
- Custom models require Provisioned Throughput to be used
- Billing continues until Provisioned Throughput is deleted
- Each model's specific pricing can be found in the Amazon Bedrock console under Model providers
- No upfront fees or minimum commitments are required for the basic pay-as-you-go model

Sources:
- [Amazon Bedrock Pricing Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-pricing.html)
- [Provisioned Throughput Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)