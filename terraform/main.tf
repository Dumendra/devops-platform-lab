provider "aws" {
  region = var.aws_region
}

module "ecr" {
  source       = "./modules/ecr"
  for_each     = toset(var.services)
  name         = "${var.repository_prefix}-${each.key}"
  force_delete = var.force_delete
  tags         = local.tags
}

module "github_oidc" {
  source          = "./modules/github_oidc"
  role_name       = "${var.repository_prefix}-ci"
  github_org      = var.github_org
  github_repo     = var.github_repo
  repository_arns = [for repo in module.ecr : repo.arn]
  tags            = local.tags
}
