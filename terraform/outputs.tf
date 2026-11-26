output "repository_urls" {
  description = "ECR URLs keyed by service name"
  value       = { for name, repo in module.ecr : name => repo.url }
}

output "ci_role_arn" {
  description = "Role ARN for GitHub Actions to assume through OIDC"
  value       = module.github_oidc.role_arn
}
