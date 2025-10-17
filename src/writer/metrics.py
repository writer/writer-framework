"""
Prometheus metrics for Writer Framework monitoring.
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from prometheus_client.core import CollectorRegistry

# Base labels for all metrics
BASE_LABELS = ['org_id', 'app_id', 'instance_type']

# HTTP request metrics
http_requests_total = Counter(
    'writer_framework_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'] + BASE_LABELS
)

http_request_duration_seconds = Histogram(
    'writer_framework_http_request_duration_seconds',
    'Duration of HTTP requests in seconds',
    ['method', 'endpoint'] + BASE_LABELS,
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

def get_metrics():
    """Get Prometheus metrics in text format, filtered to exclude bloat."""
    filtered_registry = CollectorRegistry()
    
    for collector in REGISTRY._collector_to_names:
        if hasattr(collector, '_name'):
            if collector._name in ['writer_framework_http_requests_total', 'writer_framework_http_request_duration_seconds']:
                filtered_registry.register(collector)
    
    return generate_latest(filtered_registry)

def get_metrics_content_type():
    """Get the content type for Prometheus metrics."""
    return CONTENT_TYPE_LATEST

def track_http_request(method: str, endpoint: str, status_code: int, duration_seconds: float, org_id: str = "unknown", app_id: str = "unknown", instance_type: str = "unknown"):
    """Track HTTP request metrics."""
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code),
        org_id=org_id,
        app_id=app_id,
        instance_type=instance_type
    ).inc()
    
    http_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint,
        org_id=org_id,
        app_id=app_id,
        instance_type=instance_type
    ).observe(duration_seconds)
