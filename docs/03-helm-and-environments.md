# Lesson 3: Helm and environments

## Learning goals

- Explain how a Helm chart is structured.
- Render the same chart for dev and prod and compare the output.
- Install, upgrade, and roll back a release.
- Explain how values layering supports multiple environments.

## Chart anatomy

```text
charts/platform/
  Chart.yaml
  values.yaml            defaults
  values-dev.yaml        dev overrides
  values-prod.yaml       prod overrides
  templates/             Kubernetes manifests
```

Templates used in this chart:

| Template                  | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| `_helpers.tpl`            | Names and labels shared by all resources   |
| `configmap.yaml`          | Non-sensitive service URLs                 |
| `secret.yaml`             | Database password and connection string    |
| `deployments.yaml`        | One Deployment per service                 |
| `services.yaml`           | One ClusterIP Service per service          |
| `ingress.yaml`            | Public HTTP routing                        |
| `postgres.yaml`           | StatefulSet, PVC, and headless Service      |
| `redis.yaml`              | Deployment and Service                     |
| `hpa.yaml`                | Optional CPU autoscaling                   |
| `pdb.yaml`                | Optional disruption budget                 |
| `networkpolicies.yaml`    | Optional traffic restrictions              |
| `servicemonitor.yaml`     | Optional Prometheus scrape config          |
| `grafana-dashboard.yaml`  | Optional dashboard ConfigMap               |

## Values layering

`values.yaml` provides defaults. `-f values-dev.yaml` or `-f values-prod.yaml`
overrides them. Prod sets three replicas, autoscaling, network policies,
ServiceMonitors, and a TLS-enabled Ingress. Dev keeps one replica and no
policies so it is easy to debug.

Render and compare:

```powershell
helm lint charts/platform
helm template platform charts/platform -f charts/platform/values.yaml
helm template platform charts/platform -f charts/platform/values-dev.yaml --namespace dev
helm template platform charts/platform -f charts/platform/values-prod.yaml --namespace prod
```

Redirect two renders to files and compare them with `git diff --no-index`.
Notice which resources appear only in prod.

## Install locally

After building and loading images into kind:

```powershell
helm upgrade --install platform charts/platform `
  -f charts/platform/values-dev.yaml `
  --namespace dev --create-namespace `
  --set services.gateway.tag=dev `
  --set services.orders.tag=dev `
  --set services.users.tag=dev

kubectl -n dev rollout status deployment/platform-gateway
kubectl -n dev get all,configmap,secret
helm -n dev history platform
```

Upgrade by changing a value:

```powershell
helm upgrade platform charts/platform -f charts/platform/values-dev.yaml `
  --namespace dev --set services.gateway.replicas=2
```

Roll back:

```powershell
helm -n dev rollback platform 1
```

## Why a StatefulSet for Postgres

A Deployment assumes replicas are interchangeable. A database has identity and
stable storage, so the chart uses a StatefulSet with a volume claim template.
The service is headless (`clusterIP: None`) to give pods stable DNS names.

Redis uses an emptyDir, so its data disappears when the pod is replaced. That is
acceptable for a cache, and it is a useful contrast with Postgres.

## Probes and resources

Every app container has a readiness probe on `/ready`, a liveness probe on
`/health`, CPU and memory requests, and limits. Requests affect scheduling;
limits cap usage. Setting both too high wastes capacity, and setting them too
low causes throttling or OOM kills.

## Exercises

### Exercise 3.1: Add a service value

Add `notifications` to `values.yaml` and confirm `helm template` produces its
Deployment and Service. Add a PDB entry by using the existing loop.

### Exercise 3.2: Enable guardrails in dev

Install with `-f values-prod.yaml` in a dev cluster with TLS disabled. Verify
HPAs, PDBs, NetworkPolicies, and ServiceMonitors render. Fix any policy labels
that block traffic.

### Exercise 3.3: Probe failure

Set the readiness path to `/missing` with `--set` and observe that pods are not
ready and endpoints are empty. Roll back to the previous revision.

### Exercise 3.4: Resource pressure

Lower the CPU limit to `10m` and generate traffic. Observe throttling in
`kubectl top`. Explain the difference between throttling and an OOM kill.

### Exercise 3.5: Secrets

Replace the plain Secret with a Secret created from a Kubernetes ExternalSecret
or a sealed secret. Keep `DATABASE_URL` out of Git.

## Checkpoint

You can render dev and prod, explain the differences, install and roll back a
release, and describe why Postgres and Redis use different workload types.
