import boto3
import json
import time
from datetime import datetime, timedelta

session_table_name = "restaurant-assistant-sessions"
dynamodb_resource = boto3.resource('dynamodb')

def save_session(session_id:str, messages:[],ttl_days=7):
    """
    保存session`
    :param session_id: session id
    :param messages: session messages
    :param ttl_days: session ttl days
    :return: True or False
    """
    try:
        table = dynamodb_resource.Table(session_table_name)
        # 计算TTL时间 (当前时间 + ttl_days天)
        ttl_timestamp = int((datetime.now() + timedelta(days=ttl_days)).timestamp())

        table.put_item(
            Item={
                'session_id': session_id,
                'messages': json.dumps(messages,ensure_ascii=False),
                'ttl': ttl_timestamp  
            }
        )
        return True
    except Exception as e:
        print(e)
        return False

def load_session(session_id:str):
    """
    加载session
    :param session_id: session id
    :return: session messages
    """
    try:
        table = dynamodb_resource.Table(session_table_name)
        response = table.get_item(
            Key={
                'session_id': session_id
            }
        )
        if 'Item' in response:
            return json.loads(response['Item']['messages'])
        else:
            return []
    except Exception as e:
        print(e)
        return []
