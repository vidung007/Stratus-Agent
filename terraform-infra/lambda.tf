# Corrected Lambda Function definitions

resource "aws_lambda_function" "get_status" {
  filename      = "../agent/lambda_functions/get_status.zip"
  # Use a unique function name
  function_name = "get_status_lambda-${random_string.suffix.result}"
  role          = aws_iam_role.agent_orchestrator_role.arn
  handler       = "get_status_lambda.lambda_handler"
  runtime       = "python3.12"
  source_code_hash = filebase64sha256("../agent/lambda_functions/get_status.zip")

  environment {
    variables = {
      # Refer to the unique table name directly
      "TABLE_NAME" = aws_dynamodb_table.job_results_table.name
    }
  }
}

resource "aws_lambda_function" "start_job" {
  filename      = "../agent/lambda_functions/start_job.zip"
  # Use a unique function name
  function_name = "start_job_lambda-${random_string.suffix.result}"
  role          = aws_iam_role.agent_orchestrator_role.arn
  handler       = "start_job_lambda.lambda_handler"
  runtime       = "python3.12"
  source_code_hash = filebase64sha256("../agent/lambda_functions/start_job.zip")
  
  environment {
    variables = {
      # Refer to the unique worker function name and table name
      "AGENT_FUNCTION_NAME" = aws_lambda_function.standard_agent_worker.function_name
      "TABLE_NAME"          = aws_dynamodb_table.job_results_table.name
    }
  }
}

resource "aws_lambda_function" "start_interleaved_job" {
  filename      = "../agent/lambda_functions/start_interleaved_job.zip"
  # Use a unique function name
  function_name = "start_interleaved_job_lambda-${random_string.suffix.result}"
  role          = aws_iam_role.agent_orchestrator_role.arn
  handler       = "start_interleaved_job_lambda.lambda_handler"
  runtime       = "python3.12"
  source_code_hash = filebase64sha256("../agent/lambda_functions/start_interleaved_job.zip")

  environment {
    variables = {
      # Refer to the unique worker function name and table name
      "AGENT_FUNCTION_NAME" = aws_lambda_function.interleaved_agent_worker.function_name
      "TABLE_NAME"          = aws_dynamodb_table.job_results_table.name
    }
  }
}

resource "aws_lambda_function" "standard_agent_worker" {
  # Use a unique function name
  function_name = "StandardAgentOrchestrator-${random_string.suffix.result}"
  role          = aws_iam_role.agent_orchestrator_role.arn
  image_uri     = "${aws_ecr_repository.standard_agent_worker_repo.repository_url}:latest"
  package_type  = "Image"
  timeout       = 900
  memory_size   = 1024

  environment {
    variables = {
      # Refer to the unique table name directly
      "TABLE_NAME" = aws_dynamodb_table.job_results_table.name
    }
  }
}

resource "aws_lambda_function" "interleaved_agent_worker" {
  # Use a unique function name
  function_name = "InterleavedAgentOrchestrator-${random_string.suffix.result}"
  role          = aws_iam_role.agent_orchestrator_role.arn
  image_uri     = "${aws_ecr_repository.interleaved_agent_worker_repo.repository_url}:latest"
  package_type  = "Image"
  timeout       = 900
  memory_size   = 1024

  environment {
    variables = {
      # Refer to the unique table name directly
      "TABLE_NAME" = aws_dynamodb_table.job_results_table.name
    }
  }
}