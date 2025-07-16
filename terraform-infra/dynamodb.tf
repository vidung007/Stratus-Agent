# dynamodb.tf

resource "aws_dynamodb_table" "job_results_table" {
  name         = "AgentJobResults-${random_string.suffix.result}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "jobId"

  attribute {
    name = "jobId"
    type = "S"
  }
}

# Add this block to your dynamodb.tf file, or a new .tf file

resource "aws_dynamodb_table" "my_new_table" {
  # (Required) The name of the DynamoDB table. This must be unique within your AWS account and region.
  name           = "MyNewApplicationDataTable-${random_string.suffix.result}"

  # (Required) The attribute that is used as the primary key for the table.
  # This attribute must be defined in the 'attribute' block below.
  hash_key       = "id"

  # (Required) Controls how you are charged for read and write throughput, and how you manage capacity.
  # "PROVISIONED" or "PAY_PER_REQUEST". PAY_PER_REQUEST is recommended for most new applications.
  billing_mode   = "PAY_PER_REQUEST"

  # (Required) Defines the attributes of the table.
  # The 'hash_key' and 'range_key' (if used) must be defined here.
  attribute {
    name = "id"
    type = "S" # S for String, N for Number, B for Binary
  }

  # (Optional) If you want a composite primary key (hash key + range key)
  # range_key = "timestamp"
  # attribute {
  #   name = "timestamp"
  #   type = "N"
  # }

  # (Optional) Enable server-side encryption for the table.
  server_side_encryption {
    enabled = true
  }

  # (Optional) Point-in-time recovery for the table.
  point_in_time_recovery {
    enabled = true
  }

  # (Optional) Time-to-Live (TTL) settings for the table.
  # ttl {
  #   attribute_name = "expiration_time" # Name of the attribute that stores the expiration timestamp
  #   enabled        = true
  # }

  # (Optional) Tags to apply to the table for organization and cost tracking.
  tags = {
    Environment = "Development"
    Project     = "MyApplication"
  }
}
