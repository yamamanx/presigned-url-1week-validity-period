import json
import urllib
import logging
import traceback
import util
import boto3
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()


logger = logging.getLogger()
logger.setLevel(util.logger_level())

ssm_client = boto3.client('ssm')
sns_resource = boto3.resource('sns')


def get_access_keys():
    access_keys = {
        'accesskey':'',
        'secretaccesskey':''
    }
    for key in access_keys.keys():
        response = ssm_client.get_parameter(
            Name='/presinedurl/' + key,
            WithDecryption=True
            )
        access_keys[key] = response['Parameter']['Value']
    return access_keys
    
    
def set_access_key(access_keys):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_keys['accesskey'],
        aws_secret_access_key=access_keys['secretaccesskey']
        )
    return s3_client
    
    
def get_presigned_url(s3_client, bucket, object_key):
    presigned_url = s3_client.generate_presigned_url(
        ClientMethod = 'get_object',
        Params = {
            'Bucket' : bucket, 
            'Key' : object_key

        },
        ExpiresIn = 604800,
        HttpMethod = 'GET'
    )
    return presigned_url
    
    
def get_topic_arn():
    response = ssm_client.get_parameter(
        Name='/private/private-notification'
        )
    topic_arn = response['Parameter']['Value']
    return topic_arn
    
    
def publish_topic(topic_arn, presigned_url, object_key):
    topic = sns_resource.Topic(topic_arn)
    response = topic.publish(
        Message=presigned_url,
        Subject='Presined URL for ' + object_key,
        MessageStructure='raw',
        )
    return response


def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        access_keys = get_access_keys()
        s3_client = set_access_key(access_keys)
        presigned_url = get_presigned_url(s3_client, bucket, object_key)
        topic_arn = get_topic_arn()
        publish_topic(topic_arn, presigned_url, object_key)
    
    except:
        logger.error(traceback.format_exc())
        return traceback.format_exc()
        
