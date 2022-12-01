import yaml
import aws_cdk as cdk
from constructs import Construct
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
    def __init__(self, scope:Construct, construct_id: str, yaml_path: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get configuration
        config = ReadPythonLamdbaConfig(yaml_path)
        config["entry"] = self.node.try_get_context("LAMBDA_ROOT_PATH")
        # print(f"lambda-config {config}")
        # Make Function
        lambda_function = PythonFunction(self, **config)
        self.lambda_function = lambda_function


def ReadPythonLamdbaConfig(yaml_path: str) -> dict:
    # Get configuration from yaml file
    with open(yaml_path, 'r') as file:
        row_config = yaml.safe_load(file)
    
    config={}
    config["id"] = row_config["id"]
    config["runtime"] = RUNTIMES[row_config["runtime"]]
    config["index"] = row_config["index"]
    config["handler"] = row_config["handler"]
    config["architecture"] = LAMBDA_ARCHITECTURE[row_config["architecture"]]
    config["memory_size"] = row_config["memory_size"]
    config["timeout"] = cdk.Duration.seconds(row_config["timeout"])
    config["environment"] = row_config["environment"]
    return config