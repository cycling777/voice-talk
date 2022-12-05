import yaml
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.aws_iam import Role
from aws_cdk.aws_lambda_python_alpha import PythonFunction

from utils.cdk_lambda import RUNTIMES, LAMBDA_ARCHITECTURE


class PythonLambdaStack(cdk.NestedStack):
    '''
    Creates a Python Lambda function Stack from Config YAML file
    Please call this Stack on PipelineStack or app.py

    YAML Format is below

    id: str
    runtime: str
    handler: str
    architecture: str
    memory_size: int
    timeout: int
    environment: dict
    '''

    def __init__(self, scope: Construct, construct_id: str, yaml_path: str, deploy_target: str, role: Role, environment: dict[str:str], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get configuration
        config = ReadPythonLamdbaConfig(yaml_path, deploy_target)
        config["entry"] = self.node.try_get_context("LAMBDA_ROOT_PATH")
        config["role"] = role
        config["environment"] = environment
        
                # Create Lambda function
        # print(f"lambda-config {config}")
        # Make Function
        lambda_function = PythonFunction(self, **config)

        # Add environment and permissions
        lambda_function.add_environment(
            key="DEPLOY_TARGET",
            value=deploy_target
        )
        self.lambda_function = lambda_function


def ReadPythonLamdbaConfig(yaml_path: str, deploy_target) -> dict:
    # Get configuration from yaml file
    with open(yaml_path, 'r') as file:
        row_config = yaml.safe_load(file)

    config = {}
    config["id"] = row_config["id"]
    config["function_name"] = "{}-{}" .format(
        row_config["function_name"], deploy_target)
    config["runtime"] = RUNTIMES[row_config["runtime"]]
    config["index"] = row_config["index"]
    config["handler"] = row_config["handler"]
    config["architecture"] = LAMBDA_ARCHITECTURE[row_config["architecture"]]
    config["memory_size"] = row_config["memory_size"]
    config["timeout"] = cdk.Duration.seconds(row_config["timeout"])
    config["environment"] = row_config["environment"]
    return config
