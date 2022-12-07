import aws_cdk as cdk

from websocketApp.stacks.dynamodb_table_stack import DynamodbStack
from websocketApp.stacks.websocket_applicatoin_stack import WebsocketApplicationStack


class ApplicationStage(cdk.Stage):
    def __init__(self, scope, id, *, deploy_target: str, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        # Call structure stack
        db_stack = DynamodbStack(
            self, f'DynamodbStack-{deploy_target}', deploy_target)
        websocket_applicatoin_stack = WebsocketApplicationStack(
            self, f'WebsocketApplicationStack-{deploy_target}', deploy_target)
        
        # Add grant for each resource
        websocket_applicatoin_stack.apigateway["stage"].grant_management_api_access(identity=websocket_applicatoin_stack.lambda_function["text_chat_function"])
        db_stack.dynamodb["ws_connections_table"].grant_read_write_data(grantee=websocket_applicatoin_stack.lambda_function["ws_connect_disconnect_function"])
        db_stack.dynamodb["dialogue_table"].grant_read_write_data(grantee=websocket_applicatoin_stack.lambda_function["text_chat_function"])
        db_stack.dynamodb["auth_table"].grant_read_write_data(grantee=websocket_applicatoin_stack.lambda_function["authorizer_function"])
