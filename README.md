# sidekiq-queue-monitor

Creates an AWS Lambda functions which monitors sidekiq queues. The metrics are pushed to CloudWwatch metrics and CloudWatch Alarms are set.

# Install / Update

1. Create/Update the `.env.yml` file with your security groups and subnets. See the example file.
2. Create/Update the `redis.yml` file with your redis configuration. See the example file.
3. Install/Update the infrastructure.
```bash
npm install serverless -g
npm install serverless-python-requirements

# Make sure to use your appropriate profile if have more than one profile
sls deploy <--aws-profile my-profile>  --stage prod
```