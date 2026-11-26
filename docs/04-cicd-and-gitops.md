# Lesson 4: CI/CD and GitOps

## Learning goals

- Explain each CI job and why it runs.
- Understand matrix builds, vulnerability scanning, and SBOMs.
- Describe the promotion pull request flow.
- Explain how ArgoCD reconciles desired state from Git.

## CI jobs

Open [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

1. **quality**: installs Python, runs Flake8 and Pytest.
2. **manifests**: lints and renders the Helm chart for all environments, then
   checks Terraform format and validates the configuration.
3. **images**: a matrix over `gateway`, `orders`, and `users`. Each job builds
   one image, scans it with Trivy, generates an SPDX SBOM, uploads the SBOM, and
   pushes a `sha-<commit>` image on non-PR events.

Why a matrix? A failing service is isolated, and all three builds run in
parallel. `fail-fast: false` lets you see every failure in one run.

## Scanning and SBOMs

Trivy checks operating-system and language packages against known
vulnerabilities. The workflow fails on HIGH or CRITICAL findings that have a
fix (`--ignore-unfixed`). The SBOM is an inventory of what shipped, which helps
during incident response.

Discussion points:

- Why ignore unfixed findings?
- What threshold would you choose for a regulated environment?
- How would you suppress a false positive safely?

## Image tags

Every pushed image uses `sha-<commit>`. Tags are immutable by convention: the
same tag always means the same source. This makes rollback a matter of choosing
an earlier tag.

## Promotion

The **Promote** workflow takes an image tag, opens a release branch, replaces
the `tag:` lines in `values-prod.yaml`, pushes, and opens a pull request. A human
reviews and merges it. ArgoCD then sees the new desired state.

This is deliberately slower than automatic deployment. The point is to teach
separation of concerns:

- CI decides whether code is releasable.
- A human decides what to release.
- ArgoCD makes the cluster match Git.

## ArgoCD app-of-apps

```text
argocd/root-app.yaml
  -> argocd/apps/dev.yaml      auto-sync, prune, self-heal
  -> argocd/apps/prod.yaml     manual sync
```

The root Application points at the `argocd/apps` directory. Adding a new file
there creates another Application without touching the root. This pattern is
called app-of-apps.

Both child applications point at `charts/platform` with different value files.
Dev syncs automatically. Prod requires an explicit Sync in the ArgoCD UI or CLI:

```powershell
kubectl -n argocd port-forward svc/argocd-server 8080:443
argocd app get platform-prod
argocd app sync platform-prod
argocd app wait platform-prod --health
```

## Drift and rollback

ArgoCD detects drift when someone changes the cluster directly. With
`selfHeal: true`, dev reverts it automatically. Prod compares against Git and
waits for a human.

Rollback options:

1. Revert the promotion commit and let ArgoCD sync the old tag.
2. Use `helm rollback` only for a direct Helm release, not for an ArgoCD-managed
   release.
3. Redeploy the previous image tag in the values file.

Option 1 is the GitOps answer: history in Git is the source of truth.

## Exercises

### Exercise 4.1: Break CI

Add a failing test on a branch and open a pull request. Confirm the image job
does not run. Fix the test and watch the run go green.

### Exercise 4.2: Break the scan

Introduce a vulnerable dependency in a test branch. Confirm Trivy blocks the
pipeline. Remove it and explain the finding.

### Exercise 4.3: Promote a tag

Use the CI run to find a `sha-` tag. Run the Promote workflow and review the
pull request. Merge it and watch ArgoCD sync prod after manual approval.

### Exercise 4.4: Drift

Change a Deployment replica count with `kubectl scale`. Watch dev self-heal and
prod report drift. Explain which behavior you want in each environment.

### Exercise 4.5: Rollback

Revert the promotion commit and sync prod back to the previous version. Verify
the deployed image tag with `kubectl get deployment -o yaml`.

## Checkpoint

You can trace a commit to an image, an image to a Git values change, and a Git
change to a running pod. You can explain why prod is not automatic.
