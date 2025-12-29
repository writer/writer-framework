import logging
from typing import Any, Dict, List, Optional

from writer.launchdarkly_utils import (
    LaunchDarklyEnvironment,
    get_launchdarkly_environment,
    get_launchdarkly_sdk_key,
    is_launchdarkly_enabled,
)

logger = logging.getLogger(__name__)

try:
    from ldclient import Context, LDClient
    from ldclient.config import Config

    try:
        from ldclient.observability import (  # type: ignore[import-not-found]
            ObservabilityConfig,
            ObservabilityPlugin,
        )

        OBSERVABILITY_AVAILABLE = True
    except ImportError:
        try:
            from launchdarkly.observability import (  # type: ignore[import-not-found]
                ObservabilityConfig,
                ObservabilityPlugin,
            )

            OBSERVABILITY_AVAILABLE = True
        except ImportError:
            OBSERVABILITY_AVAILABLE = False
            ObservabilityPlugin = None  # type: ignore[assignment,misc]
            ObservabilityConfig = None  # type: ignore[assignment,misc]

    LD_AVAILABLE = True
except ImportError:
    LD_AVAILABLE = False
    OBSERVABILITY_AVAILABLE = False
    LDClient = None  # type: ignore[assignment,misc]
    Config = None  # type: ignore[assignment,misc]
    Context = None  # type: ignore[assignment,misc]
    ObservabilityPlugin = None  # type: ignore[assignment,misc]
    ObservabilityConfig = None  # type: ignore[assignment,misc]


class LaunchDarklyClient:
    _client: Optional["LDClient"] = None
    _initialization_error: Optional[Exception] = None

    @classmethod
    def get_client(cls) -> Optional["LDClient"]:
        if not LD_AVAILABLE:
            return None

        if cls._client is not None:
            return cls._client

        if cls._initialization_error is not None:
            return None

        if not is_launchdarkly_enabled():
            return None

        try:
            sdk_key = get_launchdarkly_sdk_key()
            if not sdk_key:
                logger.warning("[LaunchDarkly] No SDK key available, skipping initialization")
                return None

            environment = get_launchdarkly_environment()
            from writer import VERSION

            service_version = VERSION

            if (
                OBSERVABILITY_AVAILABLE
                and ObservabilityPlugin is not None
                and ObservabilityConfig is not None
                and callable(ObservabilityPlugin)
                and callable(ObservabilityConfig)
            ):
                try:
                    observability_config = ObservabilityConfig(
                        service_name="writer-framework",
                        service_version=service_version,
                        environment=environment,
                    )
                    plugin = ObservabilityPlugin(observability_config)

                    try:
                        config = Config(sdk_key, plugins=[plugin])
                    except TypeError:
                        config = Config(sdk_key)
                        logger.warning(
                            "[LaunchDarkly] SDK version does not support plugins parameter, initializing without observability"
                        )
                except Exception as e:
                    logger.warning(
                        f"[LaunchDarkly] Failed to create observability plugin: {e}. "
                        "Initializing without observability."
                    )
                    config = Config(sdk_key)
            else:
                logger.warning(
                    "[LaunchDarkly] Observability plugin not available. "
                    "Initializing without observability support."
                )
                config = Config(sdk_key)

            cls._client = LDClient(config)

            if hasattr(cls._client, "set_tag"):
                try:
                    cls._client.set_tag("environment", environment)
                except Exception:
                    pass

            logger.info(
                f"LaunchDarkly client initialized successfully (environment: {environment})"
            )
            return cls._client

        except Exception as e:
            cls._initialization_error = e
            logger.warning(f"LaunchDarkly initialization failed: {e}", exc_info=True)
            return None

    @classmethod
    def is_available(cls) -> bool:
        return cls.get_client() is not None

    @classmethod
    def close(cls) -> None:
        if cls._client is not None:
            try:
                cls._client.close()
                logger.info("LaunchDarkly client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing LaunchDarkly client: {e}", exc_info=True)
            finally:
                cls._client = None
                cls._initialization_error = None

    @classmethod
    def build_context(
        cls,
        session_id: str,
        mode: Optional[str] = None,
        writer_application: Optional[Dict[str, Any]] = None,
    ) -> Optional["Context"]:
        if not LD_AVAILABLE or Context is None:
            return None

        try:
            org_id = None
            if writer_application and writer_application.get("organizationId"):
                try:
                    org_id = int(writer_application["organizationId"])
                except (ValueError, TypeError):
                    pass

            context_builder = Context.builder(session_id)

            if org_id is not None:
                context_builder.set("organizationId", org_id)

            if mode:
                context_builder.set("mode", mode)

            if writer_application and writer_application.get("id"):
                context_builder.set("writerApplicationId", writer_application["id"])

            return context_builder.build()

        except Exception as e:
            logger.warning(f"Failed to build LaunchDarkly context: {e}", exc_info=True)
            return None

    @classmethod
    def evaluate_flag(
        cls,
        flag_key: str,
        context: Optional["Context"],
        default: bool = False,
    ) -> bool:
        if context is None:
            return default

        try:
            client = cls.get_client()
            if client is None:
                return default

            return client.variation(flag_key, context, default)

        except Exception as e:
            logger.warning(
                f"LaunchDarkly flag evaluation failed for '{flag_key}': {e}", exc_info=True
            )
            return default

    @classmethod
    def evaluate_all_flags(
        cls,
        context: Optional["Context"],
        flag_keys: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        if context is None:
            return {}

        try:
            client = cls.get_client()
            if client is None:
                return {}

            if flag_keys is None:
                from writer.core import Config

                flag_keys = Config.feature_flags or []

            if not flag_keys:
                return {}

            return {key: cls.evaluate_flag(key, context, False) for key in flag_keys}

        except Exception as e:
            logger.warning(f"LaunchDarkly bulk flag evaluation failed: {e}", exc_info=True)
            return {}

    @classmethod
    def capture_error(
        cls,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            client = cls.get_client()
            if client is None:
                return

            if hasattr(client, "observe") and hasattr(client.observe, "record_exception"):
                client.observe.record_exception(error)
            elif hasattr(client, "_observability") and hasattr(
                client._observability, "record_exception"
            ):
                client._observability.record_exception(error)
            else:
                logger.debug("LaunchDarkly client does not support error recording")
        except Exception as e:
            logger.warning(f"Failed to capture error to LaunchDarkly: {e}", exc_info=True)
