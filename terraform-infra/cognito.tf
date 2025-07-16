# cognito.tf

resource "aws_cognito_user_pool" "agent_user_pool" {
  name = "${var.project_name}Users"
}

resource "aws_cognito_user_pool_domain" "agent_user_pool_domain" {
  domain       = "${lower(var.project_name)}-${random_string.suffix.result}"
  user_pool_id = aws_cognito_user_pool.agent_user_pool.id
}

resource "aws_cognito_user_pool_client" "express_app_client" {
  name                                 = "agent-express-server-client"
  user_pool_id                         = aws_cognito_user_pool.agent_user_pool.id
  generate_secret                      = true // This creates the client secret
  explicit_auth_flows                  = ["ALLOW_ADMIN_USER_PASSWORD_AUTH", "ALLOW_CUSTOM_AUTH", "ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  callback_urls                        = ["http://localhost:3000/auth/callback"]
  logout_urls                          = ["http://localhost:3000/login"]
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}