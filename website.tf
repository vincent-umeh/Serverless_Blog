# S3 website deployment

# Upload website files to S3
resource "aws_s3_object" "website_files" {
  for_each = fileset("${path.module}/website_files", "**/*")

  bucket       = aws_s3_bucket.website.bucket
  key          = each.value
  source       = "${path.module}/website_files/${each.value}"
  etag         = filemd5("${path.module}/website_files/${each.value}")
  content_type = lookup(local.mime_types, regex("\\.[^.]+$", each.value), "application/octet-stream")
}

# Update the app.js file with the correct API URL
resource "aws_s3_object" "app_js_with_api_url" {
  bucket       = aws_s3_bucket.website.bucket
  key          = "app.js"
  content      = replace(file("${path.module}/website_files/app.js"), "const config = {\n    apiUrl: '/api'", "const config = {\n    apiUrl: '${aws_api_gateway_deployment.blog_api_deployment.invoke_url}'")
  content_type = "application/javascript"

  depends_on = [aws_s3_object.website_files]
}

# Local variable for MIME types
locals {
  mime_types = {
    ".html" = "text/html"
    ".css"  = "text/css"
    ".js"   = "application/javascript"
    ".json" = "application/json"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".gif"  = "image/gif"
    ".svg"  = "image/svg+xml"
    ".ico"  = "image/x-icon"
  }
}