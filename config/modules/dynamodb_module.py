import yaml
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_dynamodb

from utils.cdk_dynamodb import BILLINGMODE, REMOVALPOLICY, ATTRIBUTETYPE

class ReadDynamodbTableConfig:

    def __init__(self, yaml_path: str, deploy_target: str, **kwargs):
        '''
        Creates a Dynamodb Config from Config YAML file

        YAML Format example is below
        At this moment(20221130), billing_mode can use provisioned only!!

        id: websocketConnectiontable
        table_name: TestForWebSocketConnectionsTable
        billing_mode: provisioned
        read_capacity:
            min: 2
            max: 5
        write_capacity:
            min: 2
            max: 5
        removal_policy: destroy
        partition_key:
            name: connection_id
            type: string
        sort_key:
            name: timestamp
            type: string

        '''
        # Get configuration from yaml file
        with open(yaml_path, 'r') as file:
            row_config = yaml.safe_load(file)
        
        # Set configuration
        config={}
        config["id"] = row_config["id"]
        config["table_name"] = "{}-{}".format(row_config["table_name"], deploy_target)
        config["billing_mode"] = BILLINGMODE[row_config["billing_mode"]]
        config["removal_policy"] = REMOVALPOLICY[row_config["removal_policy"]]
        config["partition_key"] = aws_dynamodb.Attribute(
            name=row_config["partition_key"]["name"],
            type=ATTRIBUTETYPE[row_config["partition_key"]["type"]]
        )
        if row_config.get("sort_key"):
            config["sort_key"] = aws_dynamodb.Attribute(
                name=row_config["sort_key"]["name"],
                type=ATTRIBUTETYPE[row_config["sort_key"]["type"]]
            )
        
        # Set Capacity Config
        capacity_config={}
        capacity_config["read_capacity"] = row_config["read_capacity"]
        capacity_config["write_capacity"] = row_config["write_capacity"]

        # create attribute
        self.config = config
        self.capacity_config = capacity_config
    
    def auto_scaling(self, dynamodb_table: aws_dynamodb.Table):
        if self.capacity_config['read_capacity']['min'] != self.capacity_config['read_capacity']['max']:
            dynamodb_table.auto_scale_read_capacity(
                max_capacity = self.capacity_config['read_capacity']['max'],
                min_capacity = self.capacity_config['read_capacity']['min'],
            ).scale_on_utilization(
                target_utilization_percent = self.capacity_config['read_capacity']['target_utilization_percent']
            )

        if self.capacity_config['write_capacity']['min'] != self.capacity_config['write_capacity']['max']:
            dynamodb_table.auto_scale_write_capacity(
                max_capacity = self.capacity_config['write_capacity']['max'],
                min_capacity = self.capacity_config['write_capacity']['min'],
            ).scale_on_utilization(
                target_utilization_percent = self.capacity_config['write_capacity']['target_utilization_percent']
            )
