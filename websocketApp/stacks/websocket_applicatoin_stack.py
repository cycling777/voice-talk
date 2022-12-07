import aws_cdk.aws_ssm as ssm
from constructs import Construct
from aws_cdk import aws_apigatewayv2_alpha as apigwv2alpha

from .lambda_stack import LambdaStack
from config.modules.apigatewayv2_alpha_ws_module import ReadApigatewayConfig


class WebsocketApplicationStack(LambdaStack):
    def __init__(self, scope: Construct, id: str, deploy_target: str, **kwargs) -> None:
        super().__init__(scope, id, deploy_target, **kwargs)

        # Get file names for deploy_target
        apigateway_file_names = self.node.try_get_context(
            deploy_target)["config_file_names"]["apigateway"]

        # Get confiuration file path
        websocket_apigateway_file_path = f'config/{deploy_target}/apigateway/{apigateway_file_names["websocket_apigateway"]}'

        websocket_apigateway_config = ReadApigatewayConfig(
            yaml_path=websocket_apigateway_file_path,
            deploy_target=deploy_target,
            connect_function=self.lambda_function["ws_connect_disconnect_function"],
            disconnect_function=self.lambda_function["ws_connect_disconnect_function"]
        )

        # Create Instances
        websocket_api = apigwv2alpha.WebSocketApi(
            self, **websocket_apigateway_config.config)

        websocket_stage = apigwv2alpha.WebSocketStage(
            self,
            id=f'WebsocketAPI-stage-{deploy_target}',
            web_socket_api=websocket_api,
            stage_name=deploy_target,
            auto_deploy=True
        )

        # Return Insatnces
        self.apigateway = {
            "api": websocket_api,
            "stage": websocket_stage
        }

        ssm.StringParameter(
            self,
            id=f"WebsocketStageURL-{deploy_target}",
            parameter_name=f"/WebsocketAPI/{deploy_target}/StageURL",
            string_value=websocket_stage.url,
            description=f"Websocket Stage URL at {deploy_target} Environment"
        )