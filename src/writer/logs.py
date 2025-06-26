import io
import json
import logging
import logging.config
import os
import sys
import time
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from writer.core import WriterState


WF_LOG = os.getenv("WF_LOG", "INFO")
WF_ENV = os.getenv("WF_ENV", "local")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord, **kwargs) -> str:
        super(JSONFormatter, self).format(record)
        # if record.args.0 is a dict add to the json dict
        data = {
            "message": record.message,
            "name": record.name,
            "module": record.module,
            "processName": record.processName,
            "threadName": record.threadName,
            "severity": record.levelname.upper()
        }
        if isinstance(record.args, dict):
            data.update(record.args)

        if isinstance(record.args, tuple):
            if len(record.args) > 0 and isinstance(record.args[0], dict):
                data.update(record.args[0])

        return json.dumps(data)


class LocalFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        super(LocalFormatter, self).format(record)
        return f"{record.levelname}[{record.name}]: {record.msg}\n"


ENV_TO_FORMATTER = {
    "local": (logging.Formatter, "local_formatter"),
    "prod": (JSONFormatter, "json_formatter"),
}


def get_formatter(env: str = WF_ENV, as_str: bool = False):
    if as_str:
        return ENV_TO_FORMATTER[env][1]
    return ENV_TO_FORMATTER[env][0](fmt="%(levelname)s - %(message)s")


def get_handler(env: str = WF_ENV, as_dict: bool = False):
    if as_dict:
        return {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": get_formatter(env, as_str=True),
        }
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(get_formatter(env))
    return handler


def get_logger(logger_name: str | None = None, level: str = WF_LOG, env: str = WF_ENV, as_dict: bool = False):
    if as_dict:
        return {
            "handlers": ["basic"],
            "level": level,
            "propagate": False,
        }

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    handler = get_handler(env)

    logger.handlers = []
    logger.addHandler(handler)
    return logger


LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "local_formatter": {
            "format": "%(levelname)s - %(name)s - %(message)s",
        },
        "json_formatter": {
            "()": JSONFormatter,
        },
    },
    "handlers": {
        "basic": get_handler(as_dict=True),
    },
    "loggers": {
        "root": get_logger(as_dict=True),
        "writer": get_logger(as_dict=True),
        "app": get_logger(as_dict=True),
        "from_app": get_logger(as_dict=True),
        "exec_logger": get_logger(as_dict=True),
        "user_code": get_logger(as_dict=True),
    }
}

logging.basicConfig(level=WF_LOG)
logging.config.dictConfig(LOGGING_CONFIG)


def _add_routing_key(routing_key: int):
    """
    A decorator to add a `routing_key` to the `extra` dict for the logging calls.

    :param routing_key: The routing key to be added to the log record.
    """
    def inner(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if "extra" not in kwargs:
                kwargs["extra"] = {}
            kwargs["extra"]["routing_key"] = routing_key
            return func(self, *args, **kwargs)
        return wrapper
    return inner


class RoutingKeyFilter(logging.Filter):
    """
    A logging filter that allows log records to be filtered based on a routing key.
    
    The filter compares the `routing_key` attribute of the log record with the routing key
    passed during initialization.

    :param routing_key: The routing key to be added to the log record.
    """
    def __init__(self, routing_key: int):
        self._routing_key = routing_key

    def filter(self, record):
        if hasattr(record, "routing_key"):
            return record.routing_key == self._routing_key
        return False


class LoggerProxy:
    """
    A proxy class that wraps around a logger instance and modifies its behavior
    by adding a routing key to log records for logging methods (`debug`, `info`, etc.)

    :param target_logger: The logger instance being proxied.
    """
    def __init__(self, target_logger: logging.Logger):
        self._target_logger = target_logger
        self.routing_key = time.monotonic_ns()

    def __getattr__(self, attr):
        attr_value = getattr(self._target_logger, attr)
        if attr in ("debug", "info", "warning", "warn", "error", "exception", "critical"):
            attr_value = _add_routing_key(self.routing_key)(attr_value)
        return attr_value

    def __setattr__(self, attr, value):
        if attr in ["_target_logger", "routing_key"]:
            super().__setattr__(attr, value)
        else:
            setattr(self._target_logger, attr, value)


@contextmanager
def capture_logs(logger: logging.Logger, session_state: Optional["WriterState"] = None, buffer: Optional[io.StringIO] = None):
    """
    Context manager that captures logs generated by the specified logger and stores them in a buffer.

    This context manager allows logs to be captured, filtered by a routing key, and optionally
    added to a session state.

    :param logger: The logger whose logs are to be captured.
    :param session_state: An optional state object where captured logs can be stored.
    :param buffer: A buffer to capture the logs. If not provided, a new buffer will be created.

    :yields: A proxy object for the logger that captures logs with a routing key.
    """
    if buffer is None:
        buffer = io.StringIO()

    original_propagate = logger.propagate
    logger.propagate = False
    logger_proxy = LoggerProxy(logger)
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(get_formatter())
    handler.addFilter(RoutingKeyFilter(routing_key=logger_proxy.routing_key))
    logger.addHandler(handler)

    try:
        yield logger_proxy
    finally:
        logger.removeHandler(handler)
        handler.close()
        captured_logs = handler.stream.getvalue()
        if session_state is not None and captured_logs:
            session_state.add_log_entry("info", "Captured logs", captured_logs)
        logger.propagate = original_propagate
