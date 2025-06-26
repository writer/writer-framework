import io
import json
import logging
import logging.config
import os
import time
from contextlib import contextmanager, redirect_stdout
from contextvars import ContextVar
from typing import Any, Dict, Optional, Tuple

WF_LOG_LEVEL = os.getenv("WF_LOG_LEVEL", "INFO")
WF_ENV = os.getenv("WF_ENV", "local")


_stdout_routing_key: ContextVar[Optional[int]] = ContextVar("stdout_routing_key", default=None)


def get_stdout_routing_key() -> Optional[int]:
    return _stdout_routing_key.get()


_logging_routing_key: ContextVar[Optional[int]] = ContextVar("logging_routing_key", default=None)


def get_logging_routing_key() -> Optional[int]:
    return _logging_routing_key.get()


class RoutingMap():
    """
    Maintains a map of routing keys to in-memory output buffers (io.StringIO).
    Used for capturing logs or stdout output in different contexts.
    """

    def __init__(self) -> None:
        # It's not expected that this will be used without context.
        # But just in case a fail-over buffer is provided
        self._buffer_map: Dict[int, io.StringIO] = {
            -1: io.StringIO(),
        }
    
    def get_buffer(self, routing_key: Optional[int] = None) -> io.StringIO:
        """
        Retrieve the buffer associated with a routing key.

        If key is None uses a fail-over buffer
        """
        if routing_key is None:
            routing_key = -1
        return self._buffer_map[routing_key]
    
    def add_buffer(self) -> Tuple[io.StringIO, int]:
        """
        Add a new buffer with a unique routing key.
        """
        key = time.monotonic_ns()
        buffer = io.StringIO()
        self._buffer_map[key] = buffer
        return buffer, key
    
    def remove_buffer(self, key: int) -> None:
        """
        Remove the buffer associated with the specified key.
        """
        self._buffer_map.pop(key, None)


routing_map = RoutingMap()


class RoutingStream(io.StringIO):
    """
    Custom stream that re-routes stdout to the correct io.StringIO buffer
    based on the current context routing key.
    """

    def write(self, s) -> int:
        if s.strip():
            logging.getLogger("stdout").info(s)
        routing_key = get_stdout_routing_key()
        return routing_map.get_buffer(routing_key).write(s)
    
    def getvalue(self) -> str:
        routing_key = get_stdout_routing_key()
        return routing_map.get_buffer(routing_key).getvalue()


class RoutingHandler(logging.StreamHandler):
    """
    Custom logging handler that re-routes logs to different buffers
    based on the current context routing key.

    Overwritten methods are mirroring original ones from logging.StreamHandler.
    The only difference is how 'stream' object is acquired
    """

    def emit(self, record):
        try:
            msg = self.format(record)
            routing_key = get_logging_routing_key()
            stream = routing_map.get_buffer(routing_key)
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def flush(self):
        routing_key = get_logging_routing_key()
        stream = routing_map.get_buffer(routing_key)
        with self.lock:
            if stream and hasattr(stream, "flush"):
                stream.flush()


@contextmanager
def use_stdout_redirect():
    """
    Context manager that redirects stdout to a context-specific buffer.
    """

    buffer, key = routing_map.add_buffer()
    token = _stdout_routing_key.set(key)

    with redirect_stdout(RoutingStream()):
        yield buffer

    routing_map.remove_buffer(key)
    _stdout_routing_key.reset(token)


@contextmanager
def use_logging_redirect():
    """
    Context manager that redirects logging to a context-specific buffer.
    """

    buffer, key = routing_map.add_buffer()
    token = _logging_routing_key.set(key)

    yield buffer

    routing_map.remove_buffer(key)
    _logging_routing_key.reset(token)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord, **kwargs) -> str:
        super().format(record)
        data = {
            "severity": record.levelname.upper(),
            "message": record.message,
            "logger_name": record.name,
            "processName": record.processName,
        }
        if isinstance(record.args, dict):
            data.update(record.args)

        # if record.args[0] is a dict add to the json dict
        if isinstance(record.args, tuple):
            if len(record.args) > 0 and isinstance(record.args[0], dict):
                data.update(record.args[0])

        return json.dumps(data)


class LocalFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        super().format(record)
        return f"{record.levelname}[{record.name}]: {record.msg}\n"


ENV_TO_FORMATTER = {
    "local": "local_formatter",
    "prod": "json_formatter",
}


def get_formatter(env: str = WF_ENV):
    return ENV_TO_FORMATTER[env]


def get_handler(env: str = WF_ENV, level: str = WF_LOG_LEVEL):
    return {
        "level": level,
        "class": "logging.StreamHandler",
        "formatter": get_formatter(env),
    }


def get_logger(level: str = WF_LOG_LEVEL):
    return {
        "handlers": ["basic"],
        "level": level,
        "propagate": False,
    }


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
        "user_formatter": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "basic": get_handler(),
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json_formatter" if WF_ENV == "prod" else None
        },
        "routing": {
            "()": RoutingHandler,
            "formatter": "user_formatter",
        }
    },
    "loggers": {
        "root": get_logger(),
        "writer": get_logger(),
        "app": get_logger(),
        "from_app": get_logger(),
        "exec_logger": {
            "handlers": ["basic", "routing"],
            "level": "DEBUG",
            "propagate": False,
        },
        "user_code": {
            "handlers": ["basic", "routing"],
            "level": "DEBUG",
            "propagate": False,
        },
        "stdout": {
            "handlers": ["stdout"],
            "propagate": False,
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
