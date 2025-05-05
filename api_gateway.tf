# API Gateway configuration

# Create API Gateway REST API
resource "aws_api_gateway_rest_api" "blog_api" {
  name        = "blog-api"
  description = "API for serverless blog platform"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway resource for /posts
resource "aws_api_gateway_resource" "posts" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  parent_id   = aws_api_gateway_rest_api.blog_api.root_resource_id
  path_part   = "posts"
}

# API Gateway resource for /posts/{slug}
resource "aws_api_gateway_resource" "post" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  parent_id   = aws_api_gateway_resource.posts.id
  path_part   = "{slug}"
}

# GET method for /posts
resource "aws_api_gateway_method" "get_posts" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.posts.id
  http_method   = "GET"
  authorization_type = "NONE"
}

# Integration for GET /posts
resource "aws_api_gateway_integration" "get_posts_integration" {
  rest_api_id             = aws_api_gateway_rest_api.blog_api.id
  resource_id             = aws_api_gateway_resource.posts.id
  http_method             = aws_api_gateway_method.get_posts.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_posts.invoke_arn
}

# POST method for /posts
resource "aws_api_gateway_method" "create_post" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.posts.id
  http_method   = "POST"
  authorization_type = "NONE"
}

# Integration for POST /posts
resource "aws_api_gateway_integration" "create_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.blog_api.id
  resource_id             = aws_api_gateway_resource.posts.id
  http_method             = aws_api_gateway_method.create_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.create_post.invoke_arn
}

# GET method for /posts/{slug}
resource "aws_api_gateway_method" "get_post" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.post.id
  http_method   = "GET"
  authorization_type = "NONE"

  request_parameters = {
    "method.request.path.slug" = true
  }
}

# Integration for GET /posts/{slug}
resource "aws_api_gateway_integration" "get_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.blog_api.id
  resource_id             = aws_api_gateway_resource.post.id
  http_method             = aws_api_gateway_method.get_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_post.invoke_arn
}

# PUT method for /posts/{slug}
resource "aws_api_gateway_method" "update_post" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.post.id
  http_method   = "PUT"
  authorization_type = "NONE"

  request_parameters = {
    "method.request.path.slug" = true
  }
}

# Integration for PUT /posts/{slug}
resource "aws_api_gateway_integration" "update_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.blog_api.id
  resource_id             = aws_api_gateway_resource.post.id
  http_method             = aws_api_gateway_method.update_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_post.invoke_arn
}

# DELETE method for /posts/{slug}
resource "aws_api_gateway_method" "delete_post" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.post.id
  http_method   = "DELETE"
  authorization_type = "NONE"

  request_parameters = {
    "method.request.path.slug" = true
  }
}

# Integration for DELETE /posts/{slug}
resource "aws_api_gateway_integration" "delete_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.blog_api.id
  resource_id             = aws_api_gateway_resource.post.id
  http_method             = aws_api_gateway_method.delete_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.delete_post.invoke_arn
}

# Enable CORS for /posts resource
resource "aws_api_gateway_method" "posts_options" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.posts.id
  http_method   = "OPTIONS"
  authorization_type = "NONE"
}

resource "aws_api_gateway_integration" "posts_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  resource_id = aws_api_gateway_resource.posts.id
  http_method = aws_api_gateway_method.posts_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "posts_options_response" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  resource_id = aws_api_gateway_resource.posts.id
  http_method = aws_api_gateway_method.posts_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "posts_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  resource_id = aws_api_gateway_resource.posts.id
  http_method = aws_api_gateway_method.posts_options.http_method
  status_code = aws_api_gateway_method_response.posts_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Enable CORS for /posts/{slug} resource
resource "aws_api_gateway_method" "post_options" {
  rest_api_id   = aws_api_gateway_rest_api.blog_api.id
  resource_id   = aws_api_gateway_resource.post.id
  http_method   = "OPTIONS"
  authorization_type = "NONE"
}

resource "aws_api_gateway_integration" "post_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  resource_id = aws_api_gateway_resource.post.id
  http_method = aws_api_gateway_method.post_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "post_options_response" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  resource_id = aws_api_gateway_resource.post.id
  http_method = aws_api_gateway_method.post_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "post_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  resource_id = aws_api_gateway_resource.post.id
  http_method = aws_api_gateway_method.post_options.http_method
  status_code = aws_api_gateway_method_response.post_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,DELETE,OPTIONS'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "blog_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.blog_api.id
  stage_name  = "prod"

  depends_on = [
    aws_api_gateway_integration.get_posts_integration,
    aws_api_gateway_integration.create_post_integration,
    aws_api_gateway_integration.get_post_integration,
    aws_api_gateway_integration.update_post_integration,
    aws_api_gateway_integration.delete_post_integration,
    aws_api_gateway_integration.posts_options_integration,
    aws_api_gateway_integration.post_options_integration
  ]

  lifecycle {
    create_before_destroy = true
  }
}

# Lambda permissions for API Gateway
resource "aws_lambda_permission" "get_posts_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_posts.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.blog_api.execution_arn}/*/${aws_api_gateway_method.get_posts.http_method}${aws_api_gateway_resource.posts.path}"
}

resource "aws_lambda_permission" "create_post_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_post.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.blog_api.execution_arn}/*/${aws_api_gateway_method.create_post.http_method}${aws_api_gateway_resource.posts.path}"
}

resource "aws_lambda_permission" "get_post_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_post.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.blog_api.execution_arn}/*/${aws_api_gateway_method.get_post.http_method}${aws_api_gateway_resource.post.path}"
}

resource "aws_lambda_permission" "update_post_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_post.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.blog_api.execution_arn}/*/${aws_api_gateway_method.update_post.http_method}${aws_api_gateway_resource.post.path}"
}

resource "aws_lambda_permission" "delete_post_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.delete_post.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.blog_api.execution_arn}/*/${aws_api_gateway_method.delete_post.http_method}${aws_api_gateway_resource.post.path}"
}