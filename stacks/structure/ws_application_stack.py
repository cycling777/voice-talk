import yaml
import os
import aws_cdk as cdk
from constructs import Construct
# from aws_cdk.aws_apigatewayv2_authorizers_alpha import WebSocketLambdaAuthorizer
from ..component.dynamodb_table_stack import DynamodbStack
from ..component.python_lambda_stack import PythonLambdaStack
from ..component.ws_api_gateway_stack import WebsocketApigatewayStack


class WebSocketApplicationStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, ComponentDirName: str, deploy_target: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Call Stacks for artifacts in need
        connection_table_stack = DynamodbStack(
            self,
            id=f"WebsocketConnectionTable-{deploy_target}",
            yaml_path=os.path.join(ComponentDirName, "ws_connection_table.yml")
        )

        websocket_function_stack = PythonLambdaStack(
            self,
            construct_id=f"WebsocketLambda-{deploy_target}",
            yaml_path=os.path.join(ComponentDirName, "ws_lambda.yml")
        )

        # DynamoDB Table for websocket connections
        connections_table = connection_table_stack.dynamodb_table
        print("CONNECTIONS_TABLE: {}".format(connections_table.table_name))
        # Python Lambda for websocket connections
        websocket_function = websocket_function_stack.lambda_function
        websocket_function.add_environment(
            key="CONNECTIONS_TABLE",
            value=connections_table.table_name
        )

        # grant permission from connections_table to websocket_function in need
        connections_table.grant_read_write_data(websocket_function)

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

        # call Stacks for network
        websocket_apigateway_stack = WebsocketApigatewayStack(
            self,
            construct_id=f"WebSocketApiGateway-{deploy_target}",
            yaml_path=os.path.join(ComponentDirName, "ws_apigateway.yml"),
            connect_function=websocket_function,
            disconnect_function=websocket_function,
            chat_function=websocket_function,
        )

        # API Gateway for the websocket client
        websocket_api = websocket_apigateway_stack.websocket_api
