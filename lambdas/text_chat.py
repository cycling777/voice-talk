import os
import json
import boto3


API_GATEWAY_URL =  os.getenv("API_GATEWAY_URL")
REGION = os.getenv("AWS_REGION")

api_gateway_connection = boto3.client(
    service_name="websocketapigateway",
    region_name=REGION,
    endpoint_url=API_GATEWAY_URL
)

def lambda_handler(event, context):
    '''Managing the Connnectoin ID'''
    # event and context are provided from AWS Lambda invocations.
    status_code = 200
    # $connect, $disconnect or custom route key.
    route = event["requestContext"]["routeKey"]
    # Websocket connection ID.
    connection_id = event["requestContext"]["connectionId"]

    if route != "text_chat":
        # Unknown route key
        status_code = 400
        return {
            "statusCode": status_code,
            "message": "route key is not correct"
        }

    # get input stream data
    body = json.loads(event["body"])
    message = body["message"]

    # make chatting answer bellow

    if api_gateway_connection.get_connection(ConnectionId=connection_id):
        api_gateway_connection.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({
                "status_code": 200,
                "message": message
            })
        )