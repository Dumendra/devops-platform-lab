# DevOps Platform Lab

An advanced, teachable DevOps project: a multi-service platform with a real
delivery pipeline, GitOps deployment, observability, and cloud infrastructure as
code. It is the bigger follow-up to the single-service `devops-lab` project.

The goal is to understand how the pieces connect, not just run commands.

## What is different from the first lab

| First lab            | This platform lab                                      |
| -------------------- | ------------------------------------------------------ |
| One Flask API        | Three services, Postgres, Redis                        |
| Plain Kubernetes YAML| Helm chart with dev/prod values                        |
| Manual CD workflow   | ArgoCD app-of-apps with automated dev and gated prod   |
| One image            | Matrix builds, vulnerability scans, SBOMs              |
| Single health check  | Metrics, ServiceMonitors, dashboard, SLOs              |
| ECR only             | ECR per service plus GitHub OIDC role                  |

## Architecture

```text
 Internet
    |
    v
 Ingress (nginx) ---> gateway ---> orders ---> Postgres
                          | ---> users
                          | ---> Redis (cache)

 GitHub repo ---> CI ---> GHCR images (sha-tagged)
      |
      +---> ArgoCD watches Git ---> dev / prod namespaces
                 |
                 v
          Prometheus scrapes /metrics ---> Grafana

 Terraform ---> ECR repositories + GitHub OIDC role
```

The gateway is the only public service. Orders owns relational data. Users is a
simple standalone service. The gateway caches users in Redis to demonstrate a
cache and a failure mode.

## Repository layout

```text
apps/                 gateway, orders, users Flask services
common/               shared health, metrics, and config helpers
tests/                service tests
Dockerfile            one image build parameterized by SERVICE
docker-compose.yml    full local stack
charts/platform/      Helm chart with dev/prod values
argocd/               AppProject and app-of-apps manifests
terraform/            ECR modules and GitHub OIDC role
.github/workflows/    CI and promotion workflows
scripts/              local cluster bootstrap
docs/                 lessons and teaching guide
```

## Prerequisites

- Python 3.12+, Docker, Docker Compose
- kubectl, Helm, kind or minikube
- Optional: Terraform 1.6+ and AWS credentials

## Quick start: local stack

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m pytest -q
docker compose up --build
```

Endpoints:

- Gateway: <http://localhost:8080>
- Orders: <http://localhost:8081/orders>
- Users: <http://localhost:8082/users>

Try it:

```powershell
Invoke-RestMethod http://localhost:8080/api/users
Invoke-RestMethod -Method Post -Uri http://localhost:8081/orders -Body '{"item":"widget","qty":2}' -ContentType application/json
Invoke-RestMethod http://localhost:8080/api/orders
```

## Quick start: Kubernetes

Build the images with the tag used by the Helm chart and load them into kind:

```powershell
foreach ($svc in @('gateway','orders','users')) {
  docker build --build-arg SERVICE=$svc --build-arg APP_VERSION=dev -t ghcr.io/dumendra/devops-platform-lab/$svc`:dev .
  kind load docker-image ghcr.io/dumendra/devops-platform-lab/$svc`:dev --name platform-lab
}

.\scripts\bootstrap-kind.ps1
kubectl -n dev get pods,svc,ingress
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Add `127.0.0.1 platform.local` to your hosts file to use the Ingress host.

ArgoCD admin password:

```powershell
$encoded = kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded))
```

## Release flow

1. A push or pull request runs CI: lint, tests, chart validation, Terraform
   validation, image builds, Trivy scans, and SBOM generation.
2. On `main`, each image is pushed to GHCR as `sha-<commit>`.
3. The **Promote** workflow opens a pull request that updates
   `charts/platform/values-prod.yaml` with the chosen tag.
4. After review and merge, ArgoCD syncs the production application. Dev syncs
   automatically; prod stays manual until a human approves.

## Infrastructure

Terraform creates one immutable ECR repository per service with scan-on-push
and a lifecycle policy, plus an OIDC provider and IAM role that GitHub Actions
can assume without long-lived AWS keys.

```powershell
cd terraform
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Use a sandbox AWS account and run `terraform destroy` after the lesson.

## Lessons

- [01 - Architecture](docs/01-architecture.md)
- [02 - Services and local stack](docs/02-services-and-local-stack.md)
- [03 - Helm and environments](docs/03-helm-and-environments.md)
- [04 - CI/CD and GitOps](docs/04-cicd-and-gitops.md)
- [05 - Observability](docs/05-observability.md)
- [06 - Security and cloud IAM](docs/06-security-and-cloud-iam.md)
- [Teaching guide](docs/teaching-guide.md)

## Cleanup

```powershell
docker compose down -v
kind delete cluster --name platform-lab
terraform -chdir=terraform destroy
```

Never commit kubeconfig files, Terraform state, or cloud credentials.
