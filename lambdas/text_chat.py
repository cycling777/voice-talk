import boto3
import os
import json

dynamodb = boto3.client("dynamodb")

connections_table = os.getenv("CONNECTIONS_TABLE") # env var in Lambda function above.

def lambda_handler(event, context):
    '''Managing the Connnectoin ID'''
    # event and context are provided from AWS Lambda invocations.
    status_code = 200
    route = event["requestContext"]["routeKey"] # $connect, $disconnect or custom route key.

    if route == "chat":
        print("body", event["body"])
        print(type(event["body"]))
        body = json.loads(event["body"])
        message = body["message"]
        return {
            "statusCode": status_code,
            "message": message
            }
    else:
        # Unknown route key
        status_code = 400
        return {"statusCode": status_code}