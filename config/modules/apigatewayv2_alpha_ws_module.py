import yaml
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk import aws_apigatewayv2_alpha as apigwv2alpha
from aws_cdk.aws_apigatewayv2_integrations_alpha import WebSocketLambdaIntegration

class ReadApigatewayConfig:

    def __init__(
        self,
        yaml_path: str,
        deploy_target: str,
        connect_function: PythonFunction = None,
        disconnect_function: PythonFunction = None,
        **kwargs
    ):
        '''# apigwv2alpha.WebSocketApi専用の汎用モジュール

        :param yaml_path: path to YAML file for configuration
        :param deploy_target: deploy stage name
        :param connect_function: instance of lambda function for connecting websocket connection
        :param disconnect_function: instance of lambda function for disconnecting websocket connection
        :param kwargs: other keyword arguments
        :return: configuration for apigwv2alpha.WebSocketApi
        
        How to use (you can copy and paste at cdk.stack):

        ## Create configuration dictionary
        config = ReadApigatewayConfig(
            yaml_path, 
            deploy_target,
            connect_function,
            disconnect_function
        )

        ## Create websocket_api instance
        websocket_api = apigwv2alpha.WebSocketApi(self, **config)
        '''
        
        with open(yaml_path, 'r') as file:
            row_config = yaml.safe_load(file)

        config = {}
        # Read YAML configuration
        config["id"] = row_config["id"]
        config["api_name"] = f"{row_config['api_name']}-{deploy_target}"

        # Create $connect connection
        if connect_function:
            connect_function = connect_function
            if kwargs.get("authorizer"):
                authorizer = kwargs.get("authorizer")
                connect_route_options = apigwv2alpha.WebSocketRouteOptions(
                    integration=WebSocketLambdaIntegration(
                        id="ConnectIntegration",
                        handler=connect_function
                    ),
                    authorizer=authorizer
                )
            else:
                connect_route_options=apigwv2alpha.WebSocketRouteOptions(
                    integration=WebSocketLambdaIntegration(
                        id="ConnectIntegration",
                        handler=connect_function
                    )
                )  
            config["connect_route_options"] = connect_route_options
        # Create $disconnect connection
        if disconnect_function:
            disconnect_function = disconnect_function
            config["disconnect_route_options"] = apigwv2alpha.WebSocketRouteOptions(
                    integration=WebSocketLambdaIntegration(
                        id="DisconnectIntegration",
                        handler=disconnect_function
                    )
                )
        self.deploy_target = deploy_target
        self.config = config
