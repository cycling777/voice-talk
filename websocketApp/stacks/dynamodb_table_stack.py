import yaml
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_dynamodb

from config.modules.dynamodb_module import ReadDynamodbTableConfig


class DynamodbStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, deploy_target: str,**kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # Get CDK Configurations for deploy_target
        table_file_names = self.node.try_get_context(deploy_target)["config_file_names"]["dynamodb"]

        #Get confiuration file path
        ws_connections_table_yaml_path = f"config/{deploy_target}/dynamodb/{table_file_names['ws_connections_table']}"
        auth_table_yaml_path = f"config/{deploy_target}/dynamodb/{table_file_names['auth_table']}"
        dialogue_table_yaml_path = f"config/{deploy_target}/dynamodb/{table_file_names['dialogues_table']}"

        # Get configurations for each dynamodb table
        ws_connections_table_config = ReadDynamodbTableConfig(ws_connections_table_yaml_path, deploy_target)
        auth_table_config = ReadDynamodbTableConfig(auth_table_yaml_path, deploy_target)
        dialogue_table_config = ReadDynamodbTableConfig(dialogue_table_yaml_path, deploy_target)
        
        # Create table instances
        ws_connections_table = aws_dynamodb.Table(self, **ws_connections_table_config.config)
        ws_connections_table_config.auto_scaling(ws_connections_table)

        auth_table = aws_dynamodb.Table(self, **auth_table_config.config)
        auth_table_config.auto_scaling(auth_table)

        dialogue_table = aws_dynamodb.Table(self, **dialogue_table_config.config)
        dialogue_table_config.auto_scaling(dialogue_table)

        # Return table instances
        self.dynamodb = {
            "ws_connections_table": ws_connections_table,
            "auth_table": auth_table,
            "dialogue_table": dialogue_table
        }