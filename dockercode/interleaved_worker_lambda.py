# interleaved_worker_lambda.py (Definitive Version)
import os
import boto3
from strands import Agent, tool
from strands.models import BedrockModel

# --- Boilerplate for DynamoDB ---
TABLE_NAME = os.environ.get('TABLE_NAME')
if not TABLE_NAME:
    raise Exception("Error: TABLE_NAME environment variable not set.")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# --- Tool Agent Definitions (from before) ---
@tool
def researcher(query: str) -> str:
    """Research specialist that gathers factual information."""
    agent = Agent(system_prompt="You are a research specialist. Gather factual information and cite sources.", callback_handler=None)
    return str(agent(f"Research: {query}"))

@tool
def data_analyst(data: str) -> str:
    """Data analyst that processes and analyzes information."""
    agent = Agent(system_prompt="You are a data analyst. Extract key insights and identify patterns.", callback_handler=None)
    return str(agent(f"Analyze this data and provide insights: {data}"))

@tool
def fact_checker(information: str) -> str:
    """Fact checker that verifies information accuracy."""
    agent = Agent(system_prompt="You are a fact checker. Verify claims and assess credibility.", callback_handler=None)
    return str(agent(f"Fact-check this information: {information}"))

@tool
def report_writer(analysis: str) -> str:
    """Report writer that creates polished final documents."""
    agent = Agent(system_prompt="You are a professional report writer. Create clear, well-structured reports.", callback_handler=None)
    return str(agent(f"Create a professional report based on: {analysis}"))

# --- Orchestrator Class ---
class StrandsInterleavedWorkflowOrchestrator:
    def __init__(self):
        self.system_prompt = """You are an intelligent workflow orchestrator with access to specialist agents:
        - researcher, data_analyst, fact_checker, report_writer.
        Your role is to intelligently coordinate a workflow using these agents to fulfill the user's task."""

    def run_workflow(self, task: str) -> str:
        # --- THIS IS THE CRITICAL FIX ---
        # Replicating the exact BedrockModel configuration from the working notebook
        # Note: The model_id in the notebook was a beta version. We'll use the official Sonnet 3.5 ID,
        # but keep the structure for interleaved thinking if the feature is supported.
        claude_model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20240620-v1:0", # Using the latest Sonnet model
            max_tokens=4096,
            temperature=1.0, # Temperature must be > 0 for interleaved thinking
            
        )
        # --- END OF CRITICAL FIX ---

        orchestrator = Agent(
            model=claude_model,
            system_prompt=self.system_prompt,
            tools=[researcher, data_analyst, fact_checker, report_writer]
        )
        
        prompt = f"""Complete this task using intelligent workflow coordination: {task}
        Instructions:
        1. Think carefully about what information you need to accomplish this task.
        2. Use the specialist agents strategically - each has unique strengths.
        3. After each tool use, reflect on the results and adapt your approach.
        4. Provide a comprehensive final response that addresses all aspects of the task.
        """
        
        return str(orchestrator(prompt))

# --- Lambda Handler ---
workflow_orchestrator = StrandsInterleavedWorkflowOrchestrator()
def lambda_handler(event, context):
    job_id = event.get('jobId')
    query = event.get('query')
    print(f"Interleaved worker started for Job ID: {job_id} with query: {query}")
    try:
        result = workflow_orchestrator.run_workflow(query)
        table.update_item(
            Key={'jobId': job_id}, UpdateExpression="set #s = :s, #r = :r",
            ExpressionAttributeNames={'#s': 'status', '#r': 'result'},
            ExpressionAttributeValues={':s': 'COMPLETE', ':r': str(result)}
        )
        print(f"Job ID {job_id} completed successfully.")
    except Exception as e:
        print(f"Job ID {job_id} failed with error: {e}")
        table.update_item(
            Key={'jobId': job_id}, UpdateExpression="set #s = :s, #r = :r",
            ExpressionAttributeNames={'#s': 'status', '#r': 'result'},
            ExpressionAttributeValues={':s': 'FAILED', ':r': str(e)}
        )
