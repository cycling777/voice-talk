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

        # Get config
        config_file_names = self.node.try_get_context(deploy_target)["config_file_names"]

        # Create Dynamodb stacks
        ws_connections_table_stack = DynamodbStack(
            self,
            id=f"WebsocketConnectionTable-{deploy_target}",
            deploy_target=deploy_target,
            yaml_path=os.path.join(components_dir_name, config_file_names["ws_connections_table"])
        )

        auth_table_stack = DynamodbStack(
            self,
            id=f"AuthTable-{deploy_target}",
            deploy_target=deploy_target,
            yaml_path=os.path.join(components_dir_name, config_file_names["auth_table"])
        )

        dialogue_table_stack = DynamodbStack(
            self,
            id=f"DialoguesTable-{deploy_target}",
            deploy_target=deploy_target,
            yaml_path=os.path.join(components_dir_name, config_file_names["dialogues_table"])
        )

        # Create IAM Role for lambda
        lambda_role = Role(
            self,
            id="Websocket-fuction-role",
            assumed_by=ServicePrincipal(service="lambda.amazonaws.com"),
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")
            ]
        )

        # Create environment variables for Lambda
        lambda_env_vars = {
            "DEPLOY_TARGET": deploy_target,
        }
        
        # Create lambda stacks
        ws_connect_disconnect_function_stack = PythonLambdaStack(
            self,
            construct_id=f"WebsocketConnectDisconnectLambda-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["ws_connect_disconnect_function"]),
            deploy_target=deploy_target,
            role=lambda_role,
            environment=lambda_env_vars
        )

        text_chat_function_stack = PythonLambdaStack(
            self,
            construct_id=f"TextChatLambda-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["text_chat_function"]),
            deploy_target=deploy_target,
            role=lambda_role,
            environment=lambda_env_vars
        )

        authorizer_function_stack = PythonLambdaStack(
            self,
            construct_id=f"AthorizerLambda-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["authorizer_function"]),
            deploy_target=deploy_target,
            role=lambda_role,
            environment=lambda_env_vars
        )

        # Create table Instances
        ws_connections_table = ws_connections_table_stack.dynamodb_table
        auth_table = auth_table_stack.dynamodb_table
        dialogue_table = dialogue_table_stack.dynamodb_table

        # Create function Instances
        ws_connect_disconnect_function = ws_connect_disconnect_function_stack.lambda_function
        text_chat_function = text_chat_function_stack.lambda_function
        authorizer_function = authorizer_function_stack.lambda_function

        # Create authorizer Instance
        # authorizer = WebSocketLambdaAuthorizer(
        #     id="WebSocketAuthorizer",
        #     handler=authorizer_function,
        #     identity_source=[
        #         "route.request.header.Authorization"
        #     ]

        # )

        # Create apigateway stack
        websocket_apigateway_stack = WebsocketApigatewayStack(
            self,
            construct_id=f"WebSocketApiGateway-{deploy_target}",
            yaml_path=os.path.join(components_dir_name, config_file_names["websocket_apigateway"]),
            deploy_target=deploy_target,
            connect_function=ws_connect_disconnect_function,
            disconnect_function=ws_connect_disconnect_function,
            text_chat_function=text_chat_function,
        )

        # Create API Gateway for the websocket client
        websocket_api = websocket_apigateway_stack.websocket_api

        # Add environment variables
        ws_connect_disconnect_function.add_environment(
            key="CONNECTIONS_TABLE",
            value=ws_connections_table.table_name
        )
        text_chat_function.add_environment(
            key="DIALOGUES_TABLE",
            value=dialogue_table.table_name
        )
        authorizer_function.add_environment(
            key="AUTH_TABLE",
            value=auth_table.table_name
        )

        # Add grant permission for relationships between resources
        ws_connections_table.grant_read_write_data(grantee=ws_connect_disconnect_function)
        dialogue_table.grant_read_write_data(grantee=text_chat_function)
        auth_table.grant_read_write_data(grantee=authorizer_function)