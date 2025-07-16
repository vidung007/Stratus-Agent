# get_status_lambda.py
import json
import boto3
import os

TABLE_NAME = os.environ.get('TABLE_NAME')
if not TABLE_NAME:
    raise Exception("Error: TABLE_NAME environment variable not set.")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Checks the status of a job in the DynamoDB table.
    """
    try:
        # The jobId will be passed as a query string parameter, e.g., /get-job-status?jobId=1234
        job_id = event.get('queryStringParameters', {}).get('jobId')

        if not job_id:
            return {'statusCode': 400, 'body': json.dumps({'error': 'jobId not provided.'})}

        # Query DynamoDB for the job
        response = table.get_item(Key={'jobId': job_id})
        
        item = response.get('Item')

        if not item:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Job not found.'})}

        # Return the full item (status, result, etc.)
        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
