import yaml
import os
import aws_cdk as cdk
from constructs import Construct
# from aws_cdk.aws_apigatewayv2_authorizers_alpha import WebSocketLambdaAuthorizer
from aws_cdk.aws_iam import Role, ServicePrincipal, ManagedPolicy
from ..components.dynamodb_table_stack import DynamodbStack
from ..components.python_lambda_stack import PythonLambdaStack
from ..components.ws_api_gateway_stack import WebsocketApigatewayStack


class WebSocketApplicationStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, components_dir_name: str, deploy_target: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        config_file_names = self.node.try_get_context(deploy_target)["config_file_names"]

        # Make DynamodbStack
        connections_table_stack = DynamodbStack(
            self,
            id=f"WebsocketConnectionTable-{deploy_target}",
            deploy_target=deploy_target,
            yaml_path=os.path.join(components_dir_name, config_file_names["connections_table"])
        )

        # Make IAM Role for lambda
        lambda_role = Role(
            self,
            id="Websocket-fuction-role",
            assumed_by=ServicePrincipal(service="lambda.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")
            ]
        )

        # Make environment variables for Lambda
        lambda_env_vars = {
            "DEPLOY_TARGET": deploy_target,
        }
        
        # Make Lambda stacks
        ws_connect_disconnect_function_stack = PythonLambdaStack(
            self,
            construct_id=f"WebsocketConnectDisconnectLambda-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["ws_connect_disconnect_function"]),
            deploy_target=deploy_target,
            role=lambda_role,
            environment=lambda_env_vars
        )

        ws_text_chat_function_stack = PythonLambdaStack(
            self,
            construct_id=f"WebsocketTextChatLambda-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["ws_text_chat_function"]),
            deploy_target=deploy_target,
            role=lambda_role,
            environment=lambda_env_vars
        )

        connections_table = connections_table_stack.dynamodb_table
        ws_connect_disconnect_function = ws_connect_disconnect_function_stack.lambda_function
        ws_text_chat_function = ws_text_chat_function_stack.lambda_function

        # # settings for authorizer_function
        # authorizer_function = PythonFunction(
        #     self, "authorizer", #Resource name
        #     runtime=Runtime.PYTHON_3_9, #Runtime version
        #     handler="authorizer.lambda_handler", #Execution handler in the code directory
        #     architecture=Architecture.X86, #Type of processor architecture
        #     memory_size=512, #Memory size
        #     timeout=cdk.Duration.seconds(30),
        #     code=Code.from_asset(lambda_root_path), #Directory from the root
        #     environment={}
        # )

        # # create websocket authorizer
        # authorizer = WebSocketLambdaAuthorizer(
        #     id="WebSocketAuthorizer",
        #     handler=authorizer_function,
        #     identity_source=[
        #         "route.request.header.Authorization"
        #     ]

        # )

        # Call stack for apigateway
        websocket_apigateway_stack = WebsocketApigatewayStack(
            self,
            construct_id=f"WebSocketApiGateway-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["websocket_apigateway"]),
            deploy_target=deploy_target,
            connect_function=ws_connect_disconnect_function,
            disconnect_function=ws_connect_disconnect_function,
            text_chat_function=ws_text_chat_function,
        )

        # API Gateway for the websocket client
        websocket_api = websocket_apigateway_stack.websocket_api

        # Add environment variables or grant permission for relationships between resources
        ws_connect_disconnect_function.add_environment(
            key="CONNECTIONS_TABLE",
            value=connections_table.table_name
        )
        connections_table.grant_read_write_data(
            grantee=ws_connect_disconnect_function
        )