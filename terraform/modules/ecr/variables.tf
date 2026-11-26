variable "name" {
  description = "Repository name"
  type        = string
}

variable "force_delete" {
  description = "Allow destroy when the repository still has images"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
