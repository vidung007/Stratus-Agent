# ecr.tf

resource "aws_ecr_repository" "standard_agent_worker_repo" {
  name = "standard-agent-worker"
}

resource "aws_ecr_repository" "interleaved_agent_worker_repo" {
  name = "interleaved-agent-worker"
}