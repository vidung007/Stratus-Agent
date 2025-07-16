# api_gateway.tf

resource "aws_apigatewayv2_api" "agent_http_api" {
  name          = "${var.project_name}HttpApi"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET"]
    allow_headers = ["*"]
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.agent_http_api.id
  name        = "$default"
  auto_deploy = true
}

# --- Integrations ---

resource "aws_apigatewayv2_integration" "start_job_integration" {
  api_id             = aws_apigatewayv2_api.agent_http_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.start_job.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "get_status_integration" {
  api_id             = aws_apigatewayv2_api.agent_http_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.get_status.invoke_arn
  payload_format_version = "2.0"
}

# --- Routes ---

resource "aws_apigatewayv2_route" "start_job_route" {
  api_id    = aws_apigatewayv2_api.agent_http_api.id
  route_key = "POST /standard-agent"
  target    = "integrations/${aws_apigatewayv2_integration.start_job_integration.id}"
}

resource "aws_apigatewayv2_route" "get_status_route" {
  api_id    = aws_apigatewayv2_api.agent_http_api.id
  route_key = "GET /get-job-status"
  target    = "integrations/${aws_apigatewayv2_integration.get_status_integration.id}"
}

# Add permissions for API Gateway to invoke the Lambdas
resource "aws_lambda_permission" "start_job_permission" {
  statement_id  = "AllowAPIGatewayToInvokeStartJob"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_job.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agent_http_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "get_status_permission" {
  statement_id  = "AllowAPIGatewayToInvokeGetStatus"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_status.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agent_http_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_integration" "start_interleaved_job_integration" {
  api_id             = aws_apigatewayv2_api.agent_http_api.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.start_interleaved_job.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "start_interleaved_job_route" {
  api_id    = aws_apigatewayv2_api.agent_http_api.id
  route_key = "POST /interleaved-agent"
  target    = "integrations/${aws_apigatewayv2_integration.start_interleaved_job_integration.id}"
}

resource "aws_lambda_permission" "start_interleaved_job_permission" {
  statement_id  = "AllowAPIGatewayToInvokeStartInterleavedJob"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_interleaved_job.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.agent_http_api.execution_arn}/*/*"
}