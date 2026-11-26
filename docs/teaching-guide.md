# Teaching Guide: Platform Lab

Use this guide to teach the advanced project to a cohort, mentor one learner, or
structure your own study. Assume learners finished the single-service lab or
have equivalent basics.

## Audience and prerequisites

Suitable for intermediate learners moving toward platform, SRE, or DevOps
engineering roles.

Required before starting:

- Comfort with Git, Docker, and basic Kubernetes commands.
- Basic Linux shell and one cloud provider concept.
- Ability to read a small Python file.

## Outcomes

By the end, learners can:

1. Explain a three-service architecture and its failure domains.
2. Run the full stack locally and debug service-to-service calls.
3. Render and manage dev/prod Helm values.
4. Explain CI matrix builds, image scanning, and SBOMs.
5. Deploy through ArgoCD and roll back using Git history.
6. Write Prometheus queries and define an SLO.
7. Explain OIDC-based CI authentication to AWS.
8. Present a release and an incident story with evidence.

## Eight-week plan

| Week | Topic             | Pre-work                    | Lab                                      | Artifact                       |
| ---- | ----------------- | --------------------------- | ---------------------------------------- | ------------------------------ |
| 1    | Architecture      | Read lesson 1               | Draw the request and delivery flows      | Architecture diagram           |
| 2    | Services          | Read lesson 2               | Compose stack, add an endpoint           | Passing tests and route demo   |
| 3    | Helm              | Read lesson 3               | Render dev/prod, install, roll back      | Rendered manifest diff         |
| 4    | CI                | Read lesson 4               | Break CI, fix, inspect SBOM              | Green CI run link              |
| 5    | GitOps            | Read lesson 4               | Bootstrap ArgoCD, promote a tag          | Promotion PR and sync screenshot|
| 6    | Observability     | Read lesson 5               | Add metrics, alert, and dashboard        | Alert firing proof             |
| 7    | Security and IaC  | Read lesson 6               | Terraform plan, OIDC, network policies   | Plan output and policy test    |
| 8    | Demo day          | Prepare a story             | Present release and rollback             | Portfolio walkthrough          |

## 90-minute session structure

1. **Recap (10 min)**: learners show last week's artifact.
2. **Concept (15 min)**: one idea with a diagram and a trade-off.
3. **Demo (15 min)**: instructor shows the working path.
4. **Guided lab (30 min)**: learners reproduce it with checkpoints.
5. **Break (5 min)**.
6. **Failure challenge (10 min)**: a broken probe, policy, tag, or query.
7. **Debrief (5 min)**: what broke, how it was found, what to read next.

Have the cluster and images ready before the session. Building everything live
 wastes the lab time.

## Milestones

- **M1**: can explain the architecture and failure domains.
- **M2**: local stack runs and all service tests pass.
- **M3**: dev and prod renders differ as expected; rollback works.
- **M4**: CI is green and each image has an SBOM.
- **M5**: ArgoCD shows both applications healthy and prod synced manually.
- **M6**: a PromQL query and an alert exist with an SLO document.
- **M7**: Terraform plan is clean and OIDC scheme is explained.
- **M8**: ten-minute demo with a failure and recovery narrative.

## Assessment rubric

| Criteria       | Meets                                                | Exceeds                                         |
| -------------- | ---------------------------------------------------- | ----------------------------------------------- |
| Architecture   | Explains flow and boundaries                         | Identifies failure domains and trade-offs      |
| Services       | Runs stack and explains env config                   | Adds an endpoint with tests and handles errors  |
| Helm           | Renders and rolls back releases                      | Adds a service and guardrails to the chart      |
| CI             | Green pipeline with scans and SBOMs                  | Adds signed images or policy checks             |
| GitOps         | Explains promotion and drift                         | Automates a safe rollback with Git history      |
| Observability  | Writes a rate query and an alert                     | Defines SLO and explores latency distributions  |
| Security/IaC   | Explains OIDC and network policies                   | Tightens trust policy and uses external secrets |
| Communication  | Presents the pipeline clearly                        | Tells a failure story with evidence and fix     |

## Demo day agenda

Per learner, ten minutes:

1. Architecture in one diagram (2 min).
2. CI run, image tag, and SBOM (2 min).
3. ArgoCD sync and a running pod (2 min).
4. A failure, the diagnosis, and the fix (2 min).
5. One thing you would change for production (2 min).

Prioritize the failure story. It reveals troubleshooting skill better than a
perfect happy-path demo.

## Adapting the material

For intermediate learners:

- Use the provided chart and workflows without adding new services.
- Pair on Helm templates and PromQL.
- Keep prod sync manual and network policies disabled until week 7.

For advanced learners:

- Add a fourth service with its own ECR repository.
- Replace in-memory users with a database and migrations.
- Add ArgoCD Image Updater or a promotion webhook.
- Add Cosign, Kyverno, and External Secrets.
- Add a multi-cluster promotion path with dev and prod clusters.

## Common pitfalls

- **Images not found in kind**: build with the exact chart tag and run
  `kind load docker-image`.
- **ArgoCD application stuck**: check the repo URL, branch, path, and value
  files in the Application spec.
- **Prometheus shows no targets**: confirm the ServiceMonitor label matches the
  Prometheus release selector and that `/metrics` exists.
- **Network policies break calls**: start with one policy and verify DNS egress.
- **Postgres pod pending**: the cluster needs a default StorageClass for the PVC.
- **Terraform apply errors**: use a sandbox account and confirm AWS credentials.
- **Promotion leaves prod broken**: always use an immutable SHA tag and review
  the PR before merge.

## Instructor checklist

Before the course:

- [ ] Sandbox AWS account with a budget alert.
- [ ] GitHub repo pushed with a public or team-readable GHCR package.
- [ ] kind or minikube tested on the learner OS.
- [ ] Base images pre-pulled and cluster add-ons verified.
- [ ] Known-good image tag recorded for rollback.

Each session:

- [ ] Verify the previous milestone runs.
- [ ] Demonstrate one failure before the fix.
- [ ] Ask learners to predict output before running commands.
- [ ] Capture screenshots or links as evidence.
- [ ] Clean up unused images, clusters, and AWS resources.

Do not share real credentials in slides or recordings. Rotate anything that
leaks, and teach learners to do the same.
