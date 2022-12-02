import boto3
import os

dynamodb = boto3.client("dynamodb")

# env var in Lambda function above.
connections_table = os.getenv("CONNECTIONS_TABLE")


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
