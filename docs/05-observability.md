# Lesson 5: Observability

## Learning goals

- Explain metrics, logs, and traces and when each is useful.
- Scrape the services with Prometheus using ServiceMonitors.
- Write useful PromQL queries and alerts.
- Define an SLO and an error budget for the gateway.

## What the app exposes

Every service exposes `/metrics` with two custom series:

- `http_requests_total{service,endpoint}`: a counter of handled requests.
- `app_uptime_seconds`: seconds since process start.

Prometheus also collects process and Go runtime metrics from its own exporters.
Counters only increase; use `rate()` to turn them into a per-second rate.

## Prometheus Operator flow

```text
ServiceMonitor -> Prometheus scrape targets -> time series -> alerts
```

The chart creates a ServiceMonitor per service when
`monitoring.serviceMonitor.enabled` is true. It selects Services by the same
labels used by the Deployments, so adding a service to `values.yaml`
automatically creates its monitor.

The `release: monitoring` label matches the default kube-prometheus-stack
selector. If your release has a different name, change that label.

## Useful queries

```promql
sum(rate(http_requests_total[5m])) by (service)
sum(rate(http_requests_total{service="gateway",endpoint=~"orders|users"}[5m]))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
up{job=~".*platform.*"}
```

The third query needs a histogram. Adding a duration histogram is a good
exercise because it forces you to think about latency distributions rather than
averages.

## Access the UI

```powershell
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
kubectl -n monitoring port-forward svc/monitoring-prometheus 9090:9090
```

Grafana credentials from the bootstrap script are `admin` / `admin`. Change
them for anything beyond a local lab.

The chart's dashboard ConfigMap is loaded when `monitoring.dashboard.enabled`
is true. It graphs request rate and uptime.

## Logs

```powershell
kubectl -n dev logs -f deployment/platform-gateway
kubectl -n dev logs -f deployment/platform-orders --all-containers=true
```

Gunicorn access logs go to stdout. In a larger system you would ship logs to
Loki or another central store and add a correlation ID to every request.

## Alerts and SLOs

A good alert is actionable and tied to user impact:

```yaml
groups:
  - name: platform
    rules:
      - alert: GatewayHighErrorRate
        expr: sum(rate(http_requests_total{service="gateway",endpoint="errors"}[5m])) > 0.05
        for: 5m
        labels:
          severity: page
        annotations:
          summary: Gateway error rate is above 5 percent
```

The example needs an `errors` label in the app, which is an exercise.

SLO example:

- SLI: successful gateway responses to `/api/orders` over five minutes.
- SLO: 99.5 percent successful over 30 days.
- Error budget: about 3.6 hours of allowed failure per 30 days.

Health endpoints are not the SLI because a process can be healthy while
returning wrong data.

## Exercises

### Exercise 5.1: Add a duration histogram

Use `prometheus_client.Histogram` in `common` to record request duration. Expose
it on `/metrics`, add a panel, and write a p95 query.

### Exercise 5.2: Error labels

Add an `error` label to the counter when a downstream call fails. Create the
alert above and verify it fires when orders is scaled to zero.

### Exercise 5.3: Dashboard

Add panels for request rate by service, uptime, and pod count. Explain why
pod count alone is not a user-facing metric.

### Exercise 5.4: SLO document

Write a one-page SLO with the SLI, target, error budget, and the actions to take
when the budget is half spent.

### Exercise 5.5: Tracing

Add OpenTelemetry instrumentation to the gateway and downstream services. Export
traces to Jaeger or Tempo and inspect a slow request.

## Checkpoint

You can find a scrape target, write a rate query, explain an alert, and define
an SLO that measures user experience.
