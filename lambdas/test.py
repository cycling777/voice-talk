import json


def lambda_handler(event, context):
    response = {
        'statusCode': 300,
        'body': 'This is a test from cdk pipeline',
        'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
        }
    }
    return response
