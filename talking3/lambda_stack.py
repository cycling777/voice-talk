import aws_cdk as cdk
from constructs import Construct
from aws_cdk.aws_lambda import Function, Runtime, Code

class LambdaStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Function(self, "testfunction", #Resource name
            runtime=Runtime.PYTHON_3_9, #Runtime version
            handler="test.lambda_handler", #Execution handler in the code directory
            code=Code.from_asset("src"), #Directory from the root
            environment={}, #Environment variables
        )