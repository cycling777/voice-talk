import os
import sys
import base64
import json
import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


REGION = os.getenv("AWS_REGION")
DEPLOY_TARGET = os.getenv("DEPLOY_TARGET")

ssm = boto3.client('ssm', REGION)
STAGE_URL = ssm.get_parameter(Name=f'/WebsocketAPI/{DEPLOY_TARGET}/StageURL', WithDecryption=True)["Parameter"]["Value"]
API_GATEWAY_URL = "https://" + STAGE_URL[6:]

polly_c = boto3.client('polly')
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
    
    # gpt3 part

    # text to speech by polly
    speech = convert_text_to_speech("Takumi", message)


    # make chatting answer bellow
    if api_gateway_connection.get_connection(ConnectionId=connection_id):
        logger.info(f"ConnectionId id is {connection_id}")
        status_code = 200
    else:
        logger.exception(f"Couldn't establish connection {connection_id}.")
        status_code = 503
        return {
            "statusCode": status_code,
        }
    
    try:
        api_gateway_connection.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({
            "statusCode": 200,
            "message": message,
            "type": "data:audio/mp3;base64,",
            "speech": base64.b64encode(speech).decode("utf-8"),
        })
        )
        logger.info(f"speech was sent correctly at {connection_id}")
    except:
        logger.exception("post to connection not successed")
        status_code = 504
    return {
        "statusCode": status_code
    }


def convert_text_to_speech(voice: str, text: str):
    if voice not in ["Takumi"]:
        logger.info('Only support Takumi voice')
        sys.exit(1)
    response = polly_c.synthesize_speech(
                   VoiceId=voice,
                   Engine='neural',
                   LanguageCode="ja-JP",
                   OutputFormat='mp3',
                   TextType='ssml',
                   Text = f'<speak>{text}></speak>')

    return response['AudioStream'].read()