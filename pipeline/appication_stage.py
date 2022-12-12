import aws_cdk as cdk

from websocketApp.stacks.dynamodb_table_stack import DynamodbStack
from websocketApp.stacks.websocket_applicatoin_stack import WebsocketApplicationStack


class ApplicationStage(cdk.Stage):
    def __init__(self, scope, id, *, deploy_target: str, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)

        # Call structure stacks
        db_stack = DynamodbStack(
            self, 'DynamodbStack', deploy_target)
        websocket_applicatoin_stack = WebsocketApplicationStack(
            self, 'WebsocketApplicationStack', deploy_target)

        # Add environment variables for lambda function
        websocket_applicatoin_stack.lambda_function["ws_connect_disconnect_function"].add_environment(
            key="CONNECTIONS_TABLE",
            value=db_stack.dynamodb["ws_connections_table"].table_name)
        websocket_applicatoin_stack.lambda_function["text_chat_function"].add_environment(
            key="DIALOGUES_TABLE",
            value=db_stack.dynamodb["dialogue_table"].table_name)
        websocket_applicatoin_stack.lambda_function["authorizer_function"].add_environment(
            key="AUTH_TABLE",
            value=db_stack.dynamodb["auth_table"].table_name)

        # Add grant for each resource
        db_stack.dynamodb["ws_connections_table"].grant_read_write_data(
            grantee=websocket_applicatoin_stack.lambda_function["ws_connect_disconnect_function"])
        db_stack.dynamodb["dialogue_table"].grant_read_write_data(
            grantee=websocket_applicatoin_stack.lambda_function["text_chat_function"])
        db_stack.dynamodb["auth_table"].grant_read_write_data(
            grantee=websocket_applicatoin_stack.lambda_function["authorizer_function"])
