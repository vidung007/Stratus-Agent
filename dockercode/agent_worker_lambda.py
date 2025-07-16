# agent_worker_lambda.py
import os
import boto3
from strands import Agent, tool

TABLE_NAME = os.environ.get('TABLE_NAME')
if not TABLE_NAME:
    raise Exception("Error: TABLE_NAME environment variable not set.")
    
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# --- Tool Definitions (Copied from before) ---

RESEARCH_ASSISTANT_PROMPT = """You are a specialized research assistant. Focus only on providing
factual, well-sourced information in response to research questions.
Always cite your sources when possible."""

@tool
def research_assistant(query: str) -> str:
    """Processes research-related queries."""
    try:
        research_agent = Agent(system_prompt=RESEARCH_ASSISTANT_PROMPT)
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def product_recommendation_assistant(query: str) -> str:
    """Handles product recommendation queries."""
    try:
        product_agent = Agent(
            system_prompt="""You are a specialized product recommendation assistant."""
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

@tool
def trip_planning_assistant(query: str) -> str:
    """Creates travel itineraries."""
    try:
        travel_agent = Agent(
            system_prompt="""You are a specialized travel planning assistant."""
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"

# --- Orchestrator Setup ---

MAIN_SYSTEM_PROMPT = """
You are an assistant that routes queries to specialized agents:
- For research questions -> Use the research_assistant tool
- For product recommendations -> Use the product_recommendation_assistant tool
- For travel planning -> Use the trip_planning_assistant tool
Always select the most appropriate tool based on the user's query.
"""

orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[
        research_assistant,
        product_recommendation_assistant,
        trip_planning_assistant,
    ],
)

# --- Lambda Handler ---

def lambda_handler(event, context):
    """
    This is the long-running worker. It gets the job, runs the agent,
    and saves the result to DynamoDB.
    """
    job_id = event.get('jobId')
    query = event.get('query')
    print(f"Worker started for Job ID: {job_id} with query: {query}")

    try:
        # Run the agent as before
        result = orchestrator(query)

        # Save the successful result to DynamoDB
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression="set #s = :s, #r = :r",
            ExpressionAttributeNames={
                '#s': 'status',
                '#r': 'result'
            },
            ExpressionAttributeValues={
                ':s': 'COMPLETE',
                ':r': str(result)
            }
        )
        print(f"Job ID {job_id} completed successfully.")

    except Exception as e:
        print(f"Job ID {job_id} failed with error: {e}")
        # Save the failure status to DynamoDB
        table.update_item(
            Key={'jobId': job_id},
            UpdateExpression="set #s = :s, #r = :r",
            ExpressionAttributeNames={
                '#s': 'status',
                '#r': 'result'
            },
            ExpressionAttributeValues={
                ':s': 'FAILED',
                ':r': str(e)
            }
        )
