# start_job_lambda.py
import json
import uuid
import boto3
import os

# Get the name of our long-running agent function from an environment variable
AGENT_FUNCTION_NAME = os.environ.get('AGENT_FUNCTION_NAME')
TABLE_NAME = os.environ.get('TABLE_NAME')

if not AGENT_FUNCTION_NAME or not TABLE_NAME:
    raise Exception("Error: AGENT_FUNCTION_NAME or TABLE_NAME environment variables not set.")

lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    This function starts the long-running agent and returns a job ID.
    """
    try:
        body = json.loads(event.get('body', '{}'))
        query = body.get('query')

        if not query:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Query not provided.'})}

        # 1. Generate a unique Job ID
        job_id = str(uuid.uuid4())
        print(f"Generated Job ID: {job_id}")

        # 2. Create a placeholder record in DynamoDB
        table.put_item(
            Item={
                'jobId': job_id,
                'status': 'PENDING',
                'query': query
            }
        )

        # 3. Create the payload for the long-running agent function
        payload = {
            'jobId': job_id,
            'query': query
        }

        # 4. Invoke the agent function asynchronously
        lambda_client.invoke(
            FunctionName=AGENT_FUNCTION_NAME,
            InvocationType='Event',  # This makes the call asynchronous
            Payload=json.dumps(payload)
        )

        # 5. Immediately return the Job ID to the frontend
        return {
            'statusCode': 202, # 202 Accepted is a standard response for async processing
            'body': json.dumps({'jobId': job_id})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
