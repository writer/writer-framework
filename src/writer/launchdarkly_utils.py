import logging
import os
from typing import Any, Callable, Literal, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

LaunchDarklyEnvironment = Literal["Development", "Production", "Test"]

LAUNCHDARKLY_ENV_DEVELOPMENT: LaunchDarklyEnvironment = "Development"
LAUNCHDARKLY_ENV_PRODUCTION: LaunchDarklyEnvironment = "Production"
LAUNCHDARKLY_ENV_TEST: LaunchDarklyEnvironment = "Test"

LAUNCHDARKLY_ENVIRONMENTS: tuple[LaunchDarklyEnvironment, ...] = (
    LAUNCHDARKLY_ENV_DEVELOPMENT,
    LAUNCHDARKLY_ENV_PRODUCTION,
    LAUNCHDARKLY_ENV_TEST,
)

LAUNCHDARKLY_ENV_DEFAULT: LaunchDarklyEnvironment = LAUNCHDARKLY_ENV_DEVELOPMENT

def get_launchdarkly_sdk_key() -> Optional[str]:
    sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
    if sdk_key and sdk_key.strip():
        return sdk_key.strip()
    return None


def is_launchdarkly_enabled() -> bool:
    return get_launchdarkly_sdk_key() is not None


def get_launchdarkly_environment() -> LaunchDarklyEnvironment:
    env_raw = os.getenv("LAUNCHDARKLY_ENVIRONMENT", LAUNCHDARKLY_ENV_DEFAULT)
    if env_raw in LAUNCHDARKLY_ENVIRONMENTS:
        return env_raw  # type: ignore[return-value]

    env_lower = env_raw.lower()
    if env_lower in ("development", "dev"):
        return LAUNCHDARKLY_ENV_DEVELOPMENT
    elif env_lower in ("production", "prod"):
        return LAUNCHDARKLY_ENV_PRODUCTION
    elif env_lower == "test":
        return LAUNCHDARKLY_ENV_TEST
    else:
        return LAUNCHDARKLY_ENV_DEFAULT


def get_flag_override(
    flag_key: str,
    override_source: Optional[str] = None,
) -> Optional[Any]:
    if override_source is None:
        override_source = "env"

    if override_source == "env":
        env_key = flag_key.upper().replace("-", "_").replace(".", "_")
        override_key = f"LAUNCHDARKLY_FLAG_OVERRIDE_{env_key}"
        override_value = os.getenv(override_key)

        if override_value is not None:
            override_lower = override_value.lower().strip()
            if override_lower in ("true", "1", "yes", "on"):
                return True
            elif override_lower in ("false", "0", "no", "off"):
                return False
            return override_value

    return None


def safe_flag_evaluation(
    flag_key: str,
    evaluation_func: Callable[[], T],
    default: T,
    log_errors: bool = True,
) -> T:
    try:
        return evaluation_func()
    except Exception as e:
        if log_errors:
            logger.warning(f"Feature flag evaluation failed for '{flag_key}': {e}", exc_info=True)
        return default


def evaluate_flag_with_override(
    flag_key: str,
    evaluation_func: Callable[[], T],
    default: T,
    log_override: bool = True,
) -> T:
    override = get_flag_override(flag_key)
    if override is not None:
        if isinstance(override, type(default)):
            if log_override:
                logger.debug(f"Using override for flag '{flag_key}': {override}")
            return override  # type: ignore[return-value]
        else:
            if log_override:
                logger.warning(
                    f"Override for flag '{flag_key}' has incorrect type "
                    f"(expected {type(default).__name__}, got {type(override).__name__}), "
                    "falling back to evaluation"
                )

    return safe_flag_evaluation(flag_key, evaluation_func, default)
