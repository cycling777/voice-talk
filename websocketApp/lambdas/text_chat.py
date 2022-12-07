import os
import json
import boto3


REGION = os.getenv("AWS_REGION")
DEPLOY_TARGET = os.getenv("DEPLOY_TARGET")

ssm = boto3.client('ssm', REGION)
STAGE_URL = ssm.get_parameter(Name=f'/WebsocketAPI/{DEPLOY_TARGET}/StageURL', WithDecryption=True)["Parameter"]["Value"]
API_GATEWAY_URL = "https://" + STAGE_URL[6:]

api_gateway_connection = boto3.client(
    "apigatewaymanagementapi",
    endpoint_url=API_GATEWAY_URL, # provided by the WebSocketStage stack.
    region_name=REGION
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
    print(event)
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