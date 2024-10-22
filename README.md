# TODO

## Run DeT commands
- See if everything works.

## Implement rest
- Create all in default space for now.
- Use repeated requests for now.

## Possible Improvements
- Use AWS SAM
- Handle next steps by web hook calls from DeT.

## STEPS
- RDS + Lambda (batch 1)
    - https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-lambda-tutorial.html
    - Keep both in same subnet (in VPC) for cost savings
    - Create security groups (use wizzard as described in tutorial)
    - Ensure valid execution role is created (and only 1)
    - Deploy from S3 (caly dir bedzie trzeba uploadowac na s3 przed odpaleniem)
- Daj access do S3
    - Create S3 GW endpoint in VPC:
        - https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html#create-gateway-endpoint-s3
    - Adjust execution role to allow s3 access.
    - Create separate security group for accessing s3 prefix list.



## RESOURCES

- S3
    - pai-poc-service-input0044
- VPC
    - pai-poc-vpc
    - vpc-0811ff3667e958d48
    - Subnets:
        - main-private: subnet-03a5e1d7db96f95c2
        - dummy-private: subnet-0cbe913976d461ba7 (RDS requires 2AZ network to start, even for 1AZ DEPLOYMENT)
    - Endpoint:
        - pai-poc-s3-endpoint vpce-00a22dac063c27d10
    - Routing: rtb-0fba03b7f67668cfc
- RDS
    - pai-poc-db
    - Sec Group:
        - default (sg-0a90f3d32bd811a02)
        - rds-lambda-2 (sg-0094c3977fa7dc061)
- Lambda Batch 1:
    - b1-paiStoreToPDL
    - Exec Role: b1-paiStoreToPDL-1729505543401
    - Destination: arn:aws:lambda:eu-central-1:050451385578:function:b2-transferToPAI
    - VPC:
        - vpc-0811ff3667e958d48
        - subnet: main-private
        - Groups:
            - sg-06d9466d637d40ad6 (lambda-rds-2)
            - sg-059a6cf02f49c4d2a (s3-access)
        - RDS SG:
            - lambda-rds-2 (sg-06d9466d637d40ad6) 
            - rds-lambda-2 (sg-0094c3977fa7dc061)
- Lambda Batch 2:
    - b2-transferToPAI
    - Exec Role: b2-transferToPAI-role-k226tn9p
    - Destination: arn:aws:lambda:eu-central-1:050451385578:function:b3-processActions
    - VPC: None
- Lambda Batch 3:
    - b3-processActions
    - Exec Role: b3-processActions-1729510703967
    - VPC:
        - vpc-0811ff3667e958d48
        - subnet: main-private
        - Groups:
            - sg-00b0566901fa59661 (lambda-rds-3)
        - RDS SG:
            - lambda-rds-3 (sg-00b0566901fa59661) 
            - rds-lambda-3 (sg-0322cb1d718010138) 
- Lambda Batch 3:
    - b4-createActionsReport
    - Exec Role:  b4-createActionsReport-1729511817673 
    - VPC:
        - vpc-0811ff3667e958d48 (10.1.0.0/24) | pai-poc-vpc
        - subnet: main-private
        - Group:
            - sg-049a409652238d001 (lambda-rds-4)
        - RDS SG:
            - lambda-rds-4 (sg-049a409652238d001) 
            - rds-lambda-4 (sg-0cce20f043c6f9e0f) 
- Amazon EventBridge
    - PaiBatchProcessingSchedule
    - arn:aws:scheduler:eu-central-1:050451385578:schedule/default/PaiBatchProcessingSchedule
    - Execution role: Amazon_EventBridge_Scheduler_LAMBDA_7879545e7c