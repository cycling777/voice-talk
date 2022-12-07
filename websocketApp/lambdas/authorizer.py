import boto3
import logging
from botocore.exceptions import ClientError
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dynamodb = boto3.client("dynamodb")

# env var in Lambda function above.
connections_table = os.getenv("CONNECTIONS_TABLE")


def handle_connect(user_name, table, connection_id):
    """
    Handles new connections by adding the connection ID and user name to the
    DynamoDB table.
    :param user_name: The name of the user that started the connection.
    :param table: The DynamoDB connection table.
    :param connection_id: The websocket connection ID of the new connection.
    :return: An HTTP status code that indicates the result of adding the connection
             to the DynamoDB table.
    """
    status_code = 200
    try:
        table.put_item(
            Item={'connection_id': connection_id, 'user_name': user_name})
        logger.info(
            "Added connection %s for user %s.", connection_id, user_name)
    except ClientError:
        logger.exception(
            "Couldn't add connection %s for user %s.", connection_id, user_name)
        status_code = 503
    return status_code

def lambda_handler(event, context):
    '''Managing the Connnectoin ID'''
    # event and context are provided from AWS Lambda invocations.
    status_code = 200
    # $connect, $disconnect or custom route key.
    route = event["requestContext"]["routeKey"]
    # Websocket connection ID.
    connection_id = event["requestContext"]["connectionId"]

    if route == "$connect":
        connect_device(connection_id)
    elif route == "$disconnect":
        disconnect_device(connection_id)
    else:
        # Unknown route key
        status_code = 400

    return {"statusCode": status_code}


def connect_device(connection_id):
    dynamodb.put_item(
        TableName=connections_table,
        Item={"connection_id": {"S": connection_id}}
    )


def disconnect_device(connection_id):
    dynamodb.delete_item(
        TableName=connections_table,
        Key={"connection_id": {"S": connection_id}}
    )
