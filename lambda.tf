# Lambda functions for the blog platform

# Create a zip file for the get-posts Lambda function
data "archive_file" "get_posts_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/get-posts"
  output_path = "${path.module}/lambda/get-posts.zip"
}

# Create a zip file for the get-post Lambda function
data "archive_file" "get_post_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/get-post"
  output_path = "${path.module}/lambda/get-post.zip"
}

# Create a zip file for the create-post Lambda function
data "archive_file" "create_post_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/create-post"
  output_path = "${path.module}/lambda/create-post.zip"
}

# Create a zip file for the update-post Lambda function
data "archive_file" "update_post_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/update-post"
  output_path = "${path.module}/lambda/update-post.zip"
}

# Create a zip file for the delete-post Lambda function
data "archive_file" "delete_post_lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/delete-post"
  output_path = "${path.module}/lambda/delete-post.zip"
}

# Lambda function to get all blog posts
resource "aws_lambda_function" "get_posts" {
  function_name    = "get-posts"
  filename         = data.archive_file.get_posts_lambda.output_path
  source_code_hash = data.archive_file.get_posts_lambda.output_base64sha256
  handler          = "index.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.blog_posts.name
    }
  }
}

# Lambda function to get a single blog post by slug
resource "aws_lambda_function" "get_post" {
  function_name    = "get-post"
  filename         = data.archive_file.get_post_lambda.output_path
  source_code_hash = data.archive_file.get_post_lambda.output_base64sha256
  handler          = "index.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.blog_posts.name
    }
  }
}

# Lambda function to create a new blog post
resource "aws_lambda_function" "create_post" {
  function_name    = "create-post"
  filename         = data.archive_file.create_post_lambda.output_path
  source_code_hash = data.archive_file.create_post_lambda.output_base64sha256
  handler          = "index.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.blog_posts.name
      ASSETS_BUCKET  = aws_s3_bucket.assets.bucket
    }
  }
}

# Lambda function to update an existing blog post
resource "aws_lambda_function" "update_post" {
  function_name    = "update-post"
  filename         = data.archive_file.update_post_lambda.output_path
  source_code_hash = data.archive_file.update_post_lambda.output_base64sha256
  handler          = "index.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.blog_posts.name
      ASSETS_BUCKET  = aws_s3_bucket.assets.bucket
    }
  }
}

# Lambda function to delete a blog post
resource "aws_lambda_function" "delete_post" {
  function_name    = "delete-post"
  filename         = data.archive_file.delete_post_lambda.output_path
  source_code_hash = data.archive_file.delete_post_lambda.output_base64sha256
  handler          = "index.handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_role.arn
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.blog_posts.name
    }
  }
}