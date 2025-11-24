import logging
import os
import sys
from typing import TYPE_CHECKING, Optional

from writer.observability.base import ObservabilityProvider

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)

SENTRY_ENABLED_ENV = "SENTRY_ENABLED"
SENTRY_DSN_ENV = "SENTRY_DSN"
SENTRY_ENVIRONMENT_ENV = "SENTRY_ENVIRONMENT"
SENTRY_TRACES_SAMPLE_RATE_ENV = "SENTRY_TRACES_SAMPLE_RATE"


class SentryAdapter(ObservabilityProvider):
    """Sentry observability provider adapter."""
    
    def __init__(self, app_path: Optional[str] = None):
        self._initialized = False
        self._app_path = app_path
        self._agent_id: Optional[str] = None
        self._org_id: Optional[str] = None
    
    def is_enabled(self) -> bool:
        """Check if Sentry is enabled."""
        return os.getenv(SENTRY_ENABLED_ENV, "true").lower() != "false"
    
    def _get_metadata(self) -> dict:
        """Get application metadata for Sentry tags/contexts."""
        metadata = {
            "agent_id": self._agent_id or os.getenv("WRITER_APP_ID"),
            "organization_id": self._org_id or os.getenv("WRITER_ORG_ID"),
        }
        if self._app_path:
            metadata["app_path"] = self._app_path
            metadata["app_name"] = os.path.basename(self._app_path)
        return metadata
    
    def initialize(self) -> bool:
        """Initialize Sentry SDK."""
        if self._initialized:
            return True
        
        if not self.is_enabled():
            logger.debug("Sentry is disabled via environment variable")
            return False
        
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_dsn = os.getenv(SENTRY_DSN_ENV)
            if not sentry_dsn:
                logger.debug("Sentry DSN not provided, skipping initialization")
                return False
            
            self._agent_id = os.getenv("WRITER_APP_ID")
            self._org_id = os.getenv("WRITER_ORG_ID")
            environment = os.getenv(SENTRY_ENVIRONMENT_ENV, "production")
            traces_sample_rate = float(os.getenv(SENTRY_TRACES_SAMPLE_RATE_ENV, "1.0"))
            traces_sample_rate = max(0.0, min(1.0, traces_sample_rate))
            
            metadata = self._get_metadata()
            
            def before_send(event, hint):
                """Filter sensitive data before sending to Sentry."""
                # Remove sensitive headers if present
                if "request" in event.get("contexts", {}):
                    headers = event["contexts"]["request"].get("headers", {})
                    sensitive_keys = ["authorization", "cookie", "x-api-key"]
                    for key in sensitive_keys:
                        headers.pop(key.lower(), None)
                return event
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=environment,
                traces_sample_rate=traces_sample_rate,
                integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)],
                enable_tracing=True,
                default_integrations=False,
                before_send=before_send,
            )
            
            # Set global tags and contexts
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("platform", "backend")
                scope.set_tag("framework", "writer-framework")
                if metadata["agent_id"]:
                    scope.set_tag("agent_id", metadata["agent_id"])
                if metadata["organization_id"]:
                    scope.set_tag("organization_id", metadata["organization_id"])
                if metadata.get("app_path"):
                    scope.set_tag("app_path", metadata["app_path"])
                    scope.set_context("application", {
                        "path": metadata["app_path"],
                        "name": metadata.get("app_name"),
                    })
                scope.set_context("runtime", {
                    "name": "python",
                    "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                })
            
            logger.info(f"Sentry initialized (environment: {environment})")
            self._initialized = True
            return True
            
        except ImportError:
            logger.debug("Sentry SDK not available")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}", exc_info=True)
            return False
    
    def instrument_fastapi_app(self, app: "FastAPI") -> None:
        """Instrument FastAPI app with Sentry middleware."""
        if not self._initialized:
            logger.debug("Sentry not initialized, skipping FastAPI instrumentation")
            return
        
        try:
            from fastapi import Request
            from starlette.middleware.base import BaseHTTPMiddleware
            import sentry_sdk
            
            metadata = self._get_metadata()
            
            class SentryMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request: Request, call_next):
                    with sentry_sdk.push_scope() as scope:
                        scope.set_tag("source", "fastapi_middleware")
                        scope.set_tag("http.method", request.method)
                        scope.set_tag("http.path", request.url.path)
                        
                        # Prefer header values over env vars for request context
                        agent_id = request.headers.get("x-agent-id") or metadata.get("agent_id")
                        org_id = request.headers.get("x-organization-id") or metadata.get("organization_id")
                        
                        if agent_id:
                            scope.set_tag("agent_id", agent_id)
                        if org_id:
                            scope.set_tag("organization_id", org_id)
                        if metadata.get("app_path"):
                            scope.set_tag("app_path", metadata["app_path"])
                        
                        scope.set_context("request", {
                            "method": request.method,
                            "url": str(request.url),
                            "path": request.url.path,
                            "query_params": dict(request.query_params),
                        })
                        
                        try:
                            response = await call_next(request)
                            scope.set_tag("http.status_code", response.status_code)
                            return response
                        except Exception as e:
                            scope.set_tag("error_type", type(e).__name__)
                            sentry_sdk.capture_exception(e)
                            raise
            
            app.add_middleware(SentryMiddleware)
            logger.debug("FastAPI app instrumented with Sentry middleware")
        except ImportError:
            logger.debug("FastAPI/Starlette not available for middleware")
        except RuntimeError as e:
            if "Cannot add middleware" in str(e):
                logger.warning("FastAPI app already started, middleware not added")
            else:
                logger.error(f"Failed to add Sentry middleware: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI app: {e}", exc_info=True)

