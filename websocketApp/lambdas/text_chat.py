import os
import json
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


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

    # get input stream data
    logger.info(event)
    body = json.loads(event["body"])
    message = body["message"]

    # make chatting answer bellow
    try:
        api_gateway_connection.get_connection(ConnectionId=connection_id)
    except ClientError:
        logger.exception(
            "Couldn't establish connection %s.", connection_id)
        status_code = 503

    try:
        api_gateway_connection.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({
                "statusCode": status_code,
                "message": message
            })
        )
    except APIGWPostConnectionError("Couldn't post to connection from apigateway") as e:
        logger.exception(e)
        status_code = 504
    return {
        "statusCode": status_code
    }

class APIGWPostConnectionError(Exception):
    pass