# lambda_function_standard.py
import os
from strands import Agent, tool

# --- Tool Definitions (Copied from the notebook) ---

RESEARCH_ASSISTANT_PROMPT = """You are a specialized research assistant. Focus only on providing
factual, well-sourced information in response to research questions.
Always cite your sources when possible."""

@tool
def research_assistant(query: str) -> str:
    """
    Process and respond to research-related queries.
    Args:
        query: A research question requiring factual information
    Returns:
        A detailed research answer with citations
    """
    try:
        research_agent = Agent(system_prompt=RESEARCH_ASSISTANT_PROMPT)
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def product_recommendation_assistant(query: str) -> str:
    """
    Handle product recommendation queries by suggesting appropriate products.
    Args:
        query: A product inquiry with user preferences
    Returns:
        Personalized product recommendations with reasoning
    """
    try:
        product_agent = Agent(
            system_prompt="""You are a specialized product recommendation assistant.
            Provide personalized product suggestions based on user preferences. Always cite your sources."""
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

@tool
def trip_planning_assistant(query: str) -> str:
    """
    Create travel itineraries and provide travel advice.
    Args:
        query: A travel planning request with destination and preferences
    Returns:
        A detailed travel itinerary or travel advice
    """
    try:
        travel_agent = Agent(
            system_prompt="""You are a specialized travel planning assistant.
            Create detailed travel itineraries based on user preferences."""
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"

# --- Orchestrator Setup ---

MAIN_SYSTEM_PROMPT = """
You are an assistant that routes queries to specialized agents:
- For research questions and factual information -> Use the research_assistant tool
- For product recommendations and shopping advice -> Use the product_recommendation_assistant tool
- For travel planning and itineraries -> Use the trip_planning_assistant tool
- For simple questions not requiring specialized knowledge -> Answer directly
Always select the most appropriate tool based on the user's query.
"""

# Instantiate the orchestrator globally to reuse it across invocations (improves performance)
orchestrator = Agent(
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[
        research_assistant,
        product_recommendation_assistant,
        trip_planning_assistant,
    ],
)

# --- Lambda Handler ---
import json

def lambda_handler(event, context):
    """
    The entry point for the AWS Lambda function.
    """
    # Extract the user's query from the API Gateway event
    try:
        body = json.loads(event.get('body', '{}'))
        customer_query = body.get('query')

        if not customer_query:
            return {
                'statusCode': 400,
                'body': json.dumps('Error: "query" not found in request body.')
            }

        # The orchestrator automatically determines which agent to use
        print(f"Received query: {customer_query}")
        response = orchestrator(customer_query)
        print(f"Orchestrator response: {response}")

        # Return the successful response
        return {
            'statusCode': 200,
            # We return the direct string response from the agent
            'body': json.dumps({'response': str(response)})
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Server error: {str(e)}')
        }
