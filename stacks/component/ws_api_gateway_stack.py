import yaml
import aws_cdk as cdk
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonFunction
# from aws_cdk.aws_apigatewayv2_authorizers_alpha import WebSocketLambdaAuthorizer
from aws_cdk import aws_apigatewayv2_alpha as apigwv2alpha
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration


class WebsocketApigatewayStack(cdk.NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        yaml_path: str,
        connect_function: PythonFunction,
        disconnect_function: PythonFunction,
        chat_function: PythonFunction,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get configuration
        try:
            deploy_target=self.node.try_get_context("deploy-target")
        except AttributeError:
            deploy_target="dev"
        
        config = ReadApigatewayConfig(yaml_path, deploy_target)
        # websocker routing
        websocket_api = apigwv2alpha.WebSocketApi(
            self,
            **config,
            connect_route_options=apigwv2alpha.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration(
                    id="ConnectIntegration",
                    handler=connect_function
                ),
                # authorizer=authorizer
            ),
            disconnect_route_options=apigwv2alpha.WebSocketRouteOptions(
                integration=WebSocketLambdaIntegration(
                    id="DisconnectIntegration",
                    handler=disconnect_function
                ),
            )
        )
        websocket_api.add_route(
            route_key="chat",
            integration=WebSocketLambdaIntegration(
                id="ChatIntegration",
                handler=chat_function
            )
        )

        websocket_stage = apigwv2alpha.WebSocketStage(
            self,
            id="WebsocketStage",
            web_socket_api=websocket_api,
            stage_name=deploy_target, # dev/prod
            auto_deploy=True
        )
        
        self.websocket_api = websocket_api



def ReadApigatewayConfig(yaml_path: str, deploy_target:str) -> dict:
    with open(yaml_path, 'r') as file:
        row_config = yaml.safe_load(file)
    
    config={}
    config["id"] = row_config["id"]
    config["api_name"] = "{}-{}" .format(row_config["api_name"] , deploy_target)

    return config