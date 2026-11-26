variable "role_name" {
  description = "Name of the CI role"
  type        = string
}

variable "github_org" {
  description = "GitHub owner allowed to assume the role"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository allowed to assume the role"
  type        = string
}

variable "repository_arns" {
  description = "ECR repository ARNs the role may push to"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
