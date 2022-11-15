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

data "archive_file" "lambda_my_function" {
  type             = "zip"
  source_dir      = "${path.module}/../webscraping"
  output_path      = "${path.module}/lambda.zip"
  excludes = [".terraform", "infrastructure-live/.terraform*"]
}

module "lambda" {
  source  = "cloudposse/lambda-function/aws"
  filename      = "${path.module}/lambda.zip"
  function_name = "fii-api"
  handler       = "webscraping/main.handler"
  runtime       = "python3.8"
}
