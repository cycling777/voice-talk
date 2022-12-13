import yaml
from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_iam as iam
from aws_cdk.aws_lambda import Code, LayerVersion
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from aws_cdk.aws_lambda_python_alpha import PythonFunction

from config.modules.pyhton_alpha_pythonfunction_module import ReadPythonLamdbaConfig
from utils.cdk_lambda import RUNTIMES, LAMBDA_ARCHITECTURE


class LambdaStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, deploy_target: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get file names for deploy_target
        lambda_file_names = self.node.try_get_context(
            deploy_target)["config_file_names"]["lambda"]

        # Get confiuration file path
        ws_connect_disconnect_function_file_path = f'config/{deploy_target}/lambda/{lambda_file_names["ws_connect_disconnect_function"]}'
        text_chat_function_file_path = f'config/{deploy_target}/lambda/{lambda_file_names["text_chat_function"]}'
        voice_chat_function_file_path = f'config/{deploy_target}/lambda/{lambda_file_names["voice_chat_function"]}'
        authorizer_function_file_path = f'config/{deploy_target}/lambda/{lambda_file_names["authorizer_function"]}'
        lambda_entry_path = self.node.try_get_context("LAMBDA_ROOT_PATH")

        # Create IAM Role for lambda
        lambda_role = Role(
            self,
            id="Websocket-function-role",
            assumed_by=ServicePrincipal(service="lambda.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"),
                ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMReadOnlyAccess")
            ]
        )
        # Create environment variables for Lambda
        lambda_env_vars = {
            "DEPLOY_TARGET": deploy_target,
        }

        # Create common settings for lambda
        common_config_for_lambda = {
            "deploy_target": deploy_target,
            "entry": lambda_entry_path,
            "role": lambda_role,
            "environment": lambda_env_vars
        }

        # Get configurations for each lambda and apigateway
        ws_connect_disconnect_function_config = ReadPythonLamdbaConfig(
            yaml_path=ws_connect_disconnect_function_file_path,
            **common_config_for_lambda
        )
        text_chat_function_config = ReadPythonLamdbaConfig(
            yaml_path=text_chat_function_file_path,
            **common_config_for_lambda
        )
        voice_chat_function_config = ReadPythonLamdbaConfig(
            yaml_path=voice_chat_function_file_path,
            **common_config_for_lambda
        )
        authorizer_function_config = ReadPythonLamdbaConfig(
            yaml_path=authorizer_function_file_path,
            **common_config_for_lambda
        )

        # Create lamnda instances
        ws_connect_disconnect_function = PythonFunction(
            self, **ws_connect_disconnect_function_config.config)
        text_chat_function = PythonFunction(
            self, **text_chat_function_config.config)
        voice_chat_function = PythonFunction(
            self, **voice_chat_function_config.config)
        authorizer_function = PythonFunction(
            self, **authorizer_function_config.config)
        
        # Create Lambda Layers
        open_ai_layer = LayerVersion(self,
            id = f"OpenAILambdaLayer-{deploy_target}",
            code = Code.from_asset("websocketApp/lambdas/layers/openai_module.zip"),
            compatible_runtimes=[RUNTIMES["python3.6"],RUNTIMES["python3.7"], RUNTIMES["python3.8"], RUNTIMES["python3.9"]],
            compatible_architectures=[LAMBDA_ARCHITECTURE["x86"], LAMBDA_ARCHITECTURE["arm64"]],
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Attach Layers to Lambda functions
        text_chat_function.add_layers(open_ai_layer)
        voice_chat_function.add_layers(open_ai_layer)


        # Attach Addtional Permissions
        polly_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=["polly:SynthesizeSpeech"])
        
        voice_chat_function.add_to_role_policy(polly_policy)

        # Return Instances
        self.lambda_function = {
            "ws_connect_disconnect_function": ws_connect_disconnect_function,
            "text_chat_function": text_chat_function,
            "voice_chat_function": voice_chat_function,
            "authorizer_function": authorizer_function
        }
