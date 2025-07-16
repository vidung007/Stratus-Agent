# start_interleaved_job_lambda.py
import json
import uuid
import boto3
import os

# This will point to our Interleaved Agent Worker function
AGENT_FUNCTION_NAME = os.environ.get('AGENT_FUNCTION_NAME') 
TABLE_NAME = os.environ.get('TABLE_NAME')

if not AGENT_FUNCTION_NAME or not TABLE_NAME:
    raise Exception("Error: AGENT_FUNCTION_NAME or TABLE_NAME environment variables not set.")

lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        query = body.get('query') # The 'task' from the form will be passed as 'query'

        if not query:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Query not provided.'})}

        job_id = str(uuid.uuid4())
        print(f"Generated Job ID for interleaved agent: {job_id}")

        table.put_item(Item={'jobId': job_id, 'status': 'PENDING', 'query': query})

        payload = {'jobId': job_id, 'query': query}

        lambda_client.invoke(
            FunctionName=AGENT_FUNCTION_NAME,
            InvocationType='Event',
            Payload=json.dumps(payload)
        )

        return {'statusCode': 202, 'body': json.dumps({'jobId': job_id})}
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
