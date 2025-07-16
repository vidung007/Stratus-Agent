# dynamodb.tf

resource "aws_dynamodb_table" "job_results_table" {
  name         = "AgentJobResults"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "jobId"

  attribute {
    name = "jobId"
    type = "S"
  }
}