# lambda.tf

# --- ZIP-Based Lambdas ---

resource "aws_lambda_function" "start_job" {
  function_name = "start_job_lambda"
  role          = aws_iam_role.agent_orchestrator_role.arn
  runtime       = "python3.12"
  handler       = "start_job_lambda.lambda_handler"
  
  filename         = "../agent-express-backend/lambda_functions/start_job.zip" // Assumes source is in the other folder
  source_code_hash = filebase64sha256("../agent-express-backend/start_job.zip")

  environment {
    variables = {
      AGENT_FUNCTION_NAME = aws_lambda_function.standard_agent_worker.function_name
      TABLE_NAME          = aws_dynamodb_table.job_results_table.name
    }
  }
}

resource "aws_lambda_function" "get_status" {
  function_name = "get_status_lambda"
  role          = aws_iam_role.agent_orchestrator_role.arn
  runtime       = "python3.12"
  handler       = "get_status_lambda.lambda_handler"
  
  filename         = "../agent-express-backend/lambda_functions/get_status.zip"
  source_code_hash = filebase64sha256("../agent-express-backend/get_status.zip")

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.job_results_table.name
    }
  }
}

# --- Container-Based Lambda ---

resource "aws_lambda_function" "standard_agent_worker" {
  function_name = "StandardAgentOrchestrator"
  role          = aws_iam_role.agent_orchestrator_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.standard_agent_worker_repo.repository_url}:latest"
  timeout       = 900 // 15 minutes
  memory_size   = 1024

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.job_results_table.name
    }
  }
}

# Zip-based starter lambda for the interleaved agent
resource "aws_lambda_function" "start_interleaved_job" {
  function_name = "start_interleaved_job_lambda"
  role          = aws_iam_role.agent_orchestrator_role.arn
  runtime       = "python3.12"
  handler       = "start_interleaved_job_lambda.lambda_handler"
  
  filename         = "../agent-express-backend/lambda_functions/start_interleaved_job.zip"
  source_code_hash = filebase64sha256("../agent-express-backend/start_interleaved_job.zip")

  environment {
    variables = {
      # This points to the interleaved container-based worker lambda below
      AGENT_FUNCTION_NAME = aws_lambda_function.interleaved_agent_worker.function_name
      TABLE_NAME          = aws_dynamodb_table.job_results_table.name
    }
  }
}

# Container-based worker lambda for the interleaved agent
resource "aws_lambda_function" "interleaved_agent_worker" {
  function_name = "InterleavedAgentOrchestrator"
  role          = aws_iam_role.agent_orchestrator_role.arn
  package_type  = "Image"
  # This points to the new ECR repo we will create next
  image_uri     = "${aws_ecr_repository.interleaved_agent_worker_repo.repository_url}:latest"
  timeout       = 900 // 15 minutes
  memory_size   = 1024

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.job_results_table.name
    }
  }
}