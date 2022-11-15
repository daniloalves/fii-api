terraform {
  backend "s3" {
    region = "us-east-1"
    encrypt = true
    bucket = "terraform-state.danilohalves.com.net"
    key    = "terraform_state_backend/fii-api/prod"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  profile   = "personal"
  region    = "us-east-1"
}

data "archive_file" "this" {
  type             = "zip"
  source_dir      = "${path.module}/../webscraping"
  output_path      = "${path.module}/lambda.zip"
  excludes = [".terraform", "infrastructure-live/.terraform*"]
}

module "lambda" {
  source  = "cloudposse/lambda-function/aws"
  filename      = "${path.module}/lambda.zip"
  source_code_hash = data.archive_file.this.output_base64sha256
  function_name = "fii-api"
  handler       = "main.handler"
  runtime       = "python3.8"
  timeout       = 10
  lambda_environment = {
    variables = {"PYTHONPATH": "/var/task/dependencies"}
  }
}

locals {
  create_lambda_url = true
}

variable "authorization_type" {
  type    = string
  default = "NONE" 
}

variable "cors" {
  type    = any
  default = {"allow_methods": ["GET","POST"], "allow_origins": ["*"]}
}

resource "aws_lambda_function_url" "this" {
  count = local.create_lambda_url ? 1 : 0

  function_name = module.lambda.function_name

  # Error: error creating Lambda Function URL: ValidationException
  #qualifier          = var.create_unqualified_alias_lambda_function_url ? null : aws_lambda_function.this[0].version
  authorization_type = var.authorization_type

  dynamic "cors" {
    for_each = length(keys(var.cors)) == 0 ? [] : [var.cors]

    content {
      allow_credentials = try(cors.value.allow_credentials, null)
      allow_headers     = try(cors.value.allow_headers, null)
      allow_methods     = try(cors.value.allow_methods, null)
      allow_origins     = try(cors.value.allow_origins, null)
      expose_headers    = try(cors.value.expose_headers, null)
      max_age           = try(cors.value.max_age, null)
    }
  }
}
