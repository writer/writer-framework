"""
Prometheus metrics for Writer Framework monitoring.
"""
import re
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry

BASE_LABELS = ['org_id', 'app_id', 'instance_type']

TRACKED_ROUTES = {
    '/api/health',
    '/api/export',
    '/api/import',
    '/api/autogen',
    '/api/init',
    '/api/stream',
    '/private/api/blueprints',
    '/private/api/blueprint/{id}'
}

# HTTP request metrics
http_requests_total = Counter(
    'writer_framework_http_requests_total',
    'Total number of HTTP requests',
    ['endpoint', 'status_code'] + BASE_LABELS
)

http_request_duration_seconds = Histogram(
    'writer_framework_http_request_duration_seconds',
    'Duration of HTTP requests in seconds',
    ['endpoint'] + BASE_LABELS,
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

def normalize_endpoint(path: str) -> str:
    """
    Normalize endpoint paths to reduce cardinality in metrics.
    Replaces dynamic segments (UUIDs, IDs) with placeholders.
    """
    # Replace UUIDs and numeric IDs in common patterns
    # Match /private/api/blueprint/{blueprint_id} pattern
    path = re.sub(r'/private/api/blueprint/[^/]+', '/private/api/blueprint/{id}', path)
    # Match other numeric IDs
    path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
    
    return path

def should_track_endpoint(path: str) -> bool:
    """
    Check if an endpoint should be tracked based on whitelist.
    """
    normalized_path = normalize_endpoint(path)
    return normalized_path in TRACKED_ROUTES

def get_metrics():
    """Get Prometheus metrics in text format, filtered to exclude bloat."""
    filtered_registry = CollectorRegistry()
    
    # Register only our custom metrics directly
    filtered_registry.register(http_requests_total)
    filtered_registry.register(http_request_duration_seconds)
    
    return generate_latest(filtered_registry)

def get_metrics_content_type():
    """Get the content type for Prometheus metrics."""
    return CONTENT_TYPE_LATEST

def track_http_request(method: str, endpoint: str, status_code: int, duration_seconds: float, org_id: str = "unknown", app_id: str = "unknown", instance_type: str = "unknown"):
    """Track HTTP request metrics."""
    normalized_endpoint = normalize_endpoint(endpoint)
    
    http_requests_total.labels(
        endpoint=normalized_endpoint,
        status_code=str(status_code),
        org_id=org_id,
        app_id=app_id,
        instance_type=instance_type
    ).inc()
    
    http_request_duration_seconds.labels(
        endpoint=normalized_endpoint,
        org_id=org_id,
        app_id=app_id,
        instance_type=instance_type
    ).observe(duration_seconds)
