import yaml
import aws_cdk as cdk
from aws_cdk.aws_iam import Role


from utils.cdk_lambda import RUNTIMES, LAMBDA_ARCHITECTURE

class ReadPythonLamdbaConfig:
    def __init__(self,
        yaml_path: str,
        deploy_target: str,
        entry: str = None,
        role: Role = None,
        environment: dict[str:str] =None
        ) -> None:
        '''## aws_lambda_python_alpha.PythonFunction専用汎用モジュール

        :param yaml_path: path to YAML file for configuration
        :param deploy_target: deploy stage name
        :param entry: directory path of lambda hundlers
        :param role: IAM Role for PythonFunction
        :param environment: additional environment variables
        :param kwargs: other keyword arguments
        :return: configuration for aws_lambda_python_alpha.PythonFunction
        
        ## How to use:

        ### Get configuration
        config = ReadPythonLamdbaConfig(
            yaml_path = yaml_path, 
            deploy_target = deploy_target,
            entry = self.node.try_get_context("LAMBDA_ROOT_PATH"),
            role = role,
            envitonment = environment
        )

        ### Make PythonFunction 
        lambda_function = PythonFunction(self, **config)
        '''
        # Get configuration from yaml file
        with open(yaml_path, 'r') as file:
            row_config = yaml.safe_load(file)

        config = {}
        # Create configuration from YAML FILE
        config["id"] = f'{row_config["id"]}-{deploy_target}'
        config["function_name"] = "{}-{}" .format(
            row_config["function_name"], deploy_target)
        config["runtime"] = RUNTIMES[row_config["runtime"]]
        config["index"] = row_config["index"]
        config["handler"] = row_config["handler"]
        config["architecture"] = LAMBDA_ARCHITECTURE[row_config["architecture"]]
        config["memory_size"] = row_config["memory_size"]
        config["timeout"] = cdk.Duration.seconds(row_config["timeout"])

        if row_config.get("environment"):
            config["environment"] = row_config["environment"]
        else:
            config["environment"] = {}
        

        # Create optional configuration
        if environment:
            config["environment"].update(environment)
        if entry:
            config["entry"] = entry
        if role:
            config["role"] = role

        self.config = config