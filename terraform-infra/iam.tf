# iam.tf

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "agent_orchestrator_role" {
  name               = "${var.project_name}AgentOrchestratorRole"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

resource "aws_iam_policy" "agent_permissions_policy" {
  name        = "${var.project_name}AgentPermissionsPolicy"
  description = "Policy with permissions for Lambda, Bedrock, and DynamoDB."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid      = "BedrockAndLambdaInvokeAccess",
        Effect   = "Allow",
        Action   = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "lambda:InvokeFunction"
        ],
        Resource = "*"
      },
      {
        Sid      = "DynamoDBFullAccess",
        Effect   = "Allow",
        Action   = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ],
        Resource = aws_dynamodb_table.job_results_table.arn
      },
      {
        Sid      = "CloudWatchLogsAccess",
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "agent_permissions_attachment" {
  role       = aws_iam_role.agent_orchestrator_role.name
  policy_arn = aws_iam_policy.agent_permissions_policy.arn
}