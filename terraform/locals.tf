locals {
  tags = {
    Project     = "devops-platform-lab"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
