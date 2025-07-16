# lambda_function_interleaved.py
import os
from strands import Agent, tool, BedrockModel

# --- Tool Agent Definitions ---
# These are the specialist agents that the main orchestrator will call.

@tool
def researcher(query: str) -> str:
    """Research specialist that gathers factual information."""
    agent = Agent(
        system_prompt="You are a research specialist. Gather factual information and cite sources when possible. Keep responses under 200 words.",
        callback_handler=None
    )
    return str(agent(f"Research: {query}"))

@tool
def data_analyst(data: str) -> str:
    """Data analyst that processes and analyzes information."""
    agent = Agent(
        system_prompt="You are a data analyst. Extract key insights, identify patterns, and provide analytical conclusions.",
        callback_handler=None
    )
    return str(agent(f"Analyze this data and provide insights: {data}"))

@tool
def fact_checker(information: str) -> str:
    """Fact checker that verifies information accuracy."""
    agent = Agent(
        system_prompt="You are a fact checker. Verify claims, assess credibility, and provide confidence levels.",
        callback_handler=None
    )
    return str(agent(f"Fact-check this information: {information}"))

@tool
def report_writer(analysis: str) -> str:
    """Report writer that creates polished final documents."""
    agent = Agent(
        system_prompt="You are a professional report writer. Create clear, well-structured reports with executive summaries.",
        callback_handler=None
    )
    return str(agent(f"Create a professional report based on: {analysis}"))

# --- Orchestrator Class ---
# This class sets up and runs the main workflow.

class StrandsInterleavedWorkflowOrchestrator:
    def __init__(self):
        self.system_prompt = """You are an intelligent workflow orchestrator with access to specialist agents:
        - researcher: Gathers factual information
        - data_analyst: Analyzes data and extracts insights
        - fact_checker: Verifies information accuracy
        - report_writer: Creates polished final reports
        Your role is to intelligently coordinate a workflow using these agents.
        Think step-by-step and use the tools in a logical sequence to fulfill the user's task.
        """

    def run_workflow(self, task: str, enable_interleaved_thinking: bool = True) -> str:
        if enable_interleaved_thinking:
            claude4_model = BedrockModel(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0", # Updated model ID for general availability
                max_tokens=4096,
                temperature=1.0,
                additional_request_fields={
                    "anthropic_version": "bedrock-2023-05-31", # Use a stable version string
                    "top_k": 250,
                    # NOTE: Interleaved thinking might have different beta headers or be standard now.
                    # This configuration is based on the notebook; check current AWS docs if it fails.
                    # "anthropic_beta": ["interleaved-thinking-2025-05-14"],
                }
            )
        else:
            claude4_model = BedrockModel(
                model_id="anthropic.claude-3-sonnet-20240229-v1:0",
                max_tokens=4096,
                temperature=1.0
            )

        orchestrator = Agent(
            model=claude4_model,
            system_prompt=self.system_prompt,
            tools=[researcher, data_analyst, fact_checker, report_writer]
        )
        
        prompt = f"Complete this task using intelligent workflow coordination: {task}"
        
        try:
            result = orchestrator(prompt)
            return str(result)
        except Exception as e:
            return f"Workflow failed: {e}"

# --- Lambda Handler ---
import json

# Instantiate the orchestrator once
workflow_orchestrator = StrandsInterleavedWorkflowOrchestrator()

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        task = body.get('task')
        enable_thinking = body.get('enable_interleaved_thinking', True)

        if not task:
            return {'statusCode': 400, 'body': json.dumps('Error: "task" not found in request body.')}

        print(f"Starting workflow for task: '{task}' with interleaved thinking: {enable_thinking}")
        result = workflow_orchestrator.run_workflow(task, enable_thinking)
        print("Workflow finished.")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'response': result})
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Server error: {str(e)}')
        }
