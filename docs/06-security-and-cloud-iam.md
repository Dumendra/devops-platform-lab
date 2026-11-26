# Lesson 6: Security and cloud IAM

## Learning goals

- Identify the security controls already in the project.
- Explain how NetworkPolicies restrict traffic.
- Describe why OIDC is safer than long-lived AWS keys in CI.
- Add one supply-chain control to the pipeline.

## Controls already present

| Layer      | Control                                                       |
| ---------- | ------------------------------------------------------------- |
| Image      | Multi-stage build, non-root UID 1001, no cache files          |
| Container  | Read-only root filesystem, dropped capabilities, no escalation |
| Kubernetes | Probes, resource limits, service accounts, optional PDBs      |
| Network    | Optional default-deny-style policies between components       |
| Registry   | Immutable tags, scan-on-push, lifecycle policy                |
| CI         | Least-privilege token permissions, Trivy, SBOM, Dependabot    |
| GitOps     | Human approval for production promotion                       |
| Cloud      | OIDC role scoped to one repository with short-lived credentials|

## Network policies

The prod values enable policies where:

- Only the gateway accepts traffic from outside the app label.
- Orders and users accept traffic only from the gateway.
- Postgres accepts connections only from app pods.
- Redis accepts connections only from the gateway.
- DNS egress is allowed explicitly.

A policy is allow-list based. Once a pod is selected, all traffic not allowed
by a policy is denied. Test policies before enabling them in a real cluster.

## Secrets

`charts/platform/templates/secret.yaml` puts a lab password into a Kubernetes
Secret. This is acceptable for a local lab, not for production. Better options:

- External Secrets Operator reading from AWS Secrets Manager.
- Sealed Secrets for encrypted secrets in Git.
- A cloud workload identity with IRSA.

Never log secret values, commit kubeconfigs, or print Terraform state in CI.

## GitHub OIDC to AWS

Terraform creates:

1. An IAM OIDC provider for `token.actions.githubusercontent.com`.
2. A role whose trust policy requires a matching repository claim.
3. A policy allowing ECR pushes only to the repositories in this project.

GitHub Actions requests a short-lived token and exchanges it for AWS
credentials. No AWS access key exists in GitHub secrets.

Trust policy condition:

```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": "repo:Dumendra/devops-platform-lab:*"
}
```

Restrict `*` to `ref:refs/heads/main` for a production role. That prevents a
feature branch from assuming the deploy role.

## Supply chain

- Pin action versions, ideally to commit SHAs after you trust them.
- Scan images with Trivy and track HIGH/CRITICAL findings.
- Keep SBOMs from CI for incident response.
- Sign images with Cosign and verify signatures in the cluster with Kyverno.
- Update dependencies through reviewed Dependabot pull requests.

## Exercises

### Exercise 6.1: Tighten the trust policy

Change the OIDC condition to allow only `main` and pull requests from the repo.
Plan the change and explain what access is removed.

### Exercise 6.2: Policy test

Enable network policies in dev. Verify gateway to orders works, then create a
pod without the expected labels and confirm it is blocked.

### Exercise 6.3: External secrets

Deploy External Secrets Operator, store the database password in AWS Secrets
Manager, and replace the chart Secret with an ExternalSecret.

### Exercise 6.4: Image signing

Install Cosign, sign a pushed image with keyless signing, and add a Kyverno
policy that rejects unsigned images.

### Exercise 6.5: Policy as code

Add Conftest or OPA checks that reject Deployments without resource limits,
readiness probes, or a non-root security context. Run it in CI.

## Checkpoint

You can name the controls in each layer, explain OIDC in one paragraph, and
describe one supply-chain improvement with a trade-off.
