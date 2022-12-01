import boto3
import os

dynamodb = boto3.client("dynamodb")

connections_table = os.getenv("CONNECTIONS_TABLE") # env var in Lambda function above.

def handler(event):
    '''Managing the Connnectoin ID'''
    # event and context are provided from AWS Lambda invocations.
    status_code = 200
    route = event["requestContext"]["routeKey"] # $connect, $disconnect or custom route key.
    connection_id = event["requestContext"]["connectionId"] # Websocket connection ID.

    if route == "$connect":
        connect_device(connection_id)
    elif route == "$disconnect":
        disconnect_device(connection_id)
    elif route == "chat":
        # chat message implementation.
        print("Connecting Now...")
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