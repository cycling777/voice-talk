from aws_cdk import aws_dynamodb, RemovalPolicy
from aws_cdk.aws_dynamodb import BillingMode

# CDK Configs
BILLINGMODE={
    "provisioned": BillingMode.PROVISIONED,
    "pro": BillingMode.PROVISIONED,
    "pay_per_request": BillingMode.PAY_PER_REQUEST,
}
REMOVALPOLICY={
    "destroy": RemovalPolicy.DESTROY,
    "retain": RemovalPolicy.RETAIN,
    "snapshot": RemovalPolicy.SNAPSHOT,
}
ATTRIBUTETYPE={
    "string": aws_dynamodb.AttributeType.STRING,
    "number": aws_dynamodb.AttributeType.NUMBER,
    "binary": aws_dynamodb.AttributeType.BINARY,
}