variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "blog_name" {
  description = "Name of the blog"
  type        = string
  default     = "Serverless Blog Platform"
}