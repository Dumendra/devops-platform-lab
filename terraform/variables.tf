variable "aws_region" {
  description = "AWS region for the registries and CI role"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name used in tags"
  type        = string
  default     = "dev"
}

variable "repository_prefix" {
  description = "Prefix for each ECR repository"
  type        = string
  default     = "devops-platform"
}

variable "services" {
  description = "Services that get their own ECR repository"
  type        = list(string)
  default     = ["gateway", "orders", "users"]
}

variable "force_delete" {
  description = "Allow destroy even when repositories contain images"
  type        = bool
  default     = true
}

variable "github_org" {
  description = "GitHub owner of the repository allowed to assume the CI role"
  type        = string
  default     = "Dumendra"
}

variable "github_repo" {
  description = "GitHub repository allowed to assume the CI role"
  type        = string
  default     = "devops-platform-lab"
}
