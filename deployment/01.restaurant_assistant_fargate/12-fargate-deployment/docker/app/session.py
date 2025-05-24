import boto3
import json
session_table_name = "restaurant-assistant-sessions"
dynamodb_resource = boto3.resource('dynamodb')

def save_session(session_id:str, messages:[]):
    try:
        table = dynamodb_resource.Table(session_table_name)
        table.put_item(
            Item={
                'session_id': session_id,
                'messages': json.dumps(messages,ensure_ascii=False)
            }
        )
        return True
    except Exception as e:
        print(e)
        return False

def load_session(session_id:str):
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
