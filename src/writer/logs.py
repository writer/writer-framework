import io
import json
import logging
import logging.config
import os
from contextlib import contextmanager, redirect_stdout
from time import time
from typing import Any, Callable, Dict, Optional

WRITER_LOG_LEVEL = os.getenv("WRITER_LOG_LEVEL", "INFO")
WRITER_LOG_FORMAT = os.getenv("WRITER_LOG_FORMAT", "text")  # 'text' or 'json'

FAILOVER_ROUTING_KEY = "unset"
FAILOVER_BUFFER = "failover"


def get_routing_key(prefix: Optional[str] = None) -> str:
    try:
        from writer.blueprints import get_current_block
        current_block = get_current_block()
    except RuntimeError:
        current_block = None

    key = FAILOVER_ROUTING_KEY
    if current_block is not None:
        key = current_block.component.id
    return f"{prefix}-{key}"


class RoutingMap():
    """
    Maintains a map of routing keys to in-memory output buffers (io.StringIO).
    Used for capturing logs or stdout output in different contexts.
    """

    def __init__(self) -> None:
        # It's not expected that this will be used without context.
        # But just in case a fail-over buffer is provided
        self._buffer_map: Dict[str, io.StringIO] = {
            FAILOVER_BUFFER: io.StringIO(),
        }
    
    def get_buffer(self, key: str) -> io.StringIO:
        """
        Retrieve the buffer associated with a routing key.

        If buffer for the key is not present uses a fail-over buffer
        """
        return self._buffer_map.get(key, self._buffer_map[FAILOVER_BUFFER])

    def add_buffer(self, key: str) -> io.StringIO:
        """
        Add a new buffer with the given key.
        """
        buffer = io.StringIO()
        self._buffer_map[key] = buffer
        return buffer

    def remove_buffer(self, key: str) -> None:
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

    def write(self, s: str) -> int:
        if s.strip():
            logging.getLogger("stdout").info(s)
        routing_key = get_routing_key(prefix="stdout")
        return routing_map.get_buffer(routing_key).write(s)
    
    def getvalue(self) -> str:
        routing_key = get_routing_key(prefix="stdout")
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
            routing_key = get_routing_key(prefix="logging")
            stream = routing_map.get_buffer(routing_key)
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def flush(self):
        routing_key = get_routing_key(prefix="logging")
        stream = routing_map.get_buffer(routing_key)
        with self.lock:
            if stream and hasattr(stream, "flush"):
                stream.flush()


@contextmanager
def use_stdout_redirect(add_log_entry_func: Callable[[str], None]):
    """
    Context manager that redirects stdout to a context-specific buffer.
    """

    key = get_routing_key(prefix="stdout")
    buffer = routing_map.add_buffer(key)
    try:
        with redirect_stdout(RoutingStream()):
            yield buffer
    finally:
        routing_map.remove_buffer(key)
        stdout = buffer.getvalue()
        if stdout:
            add_log_entry_func(stdout)


@contextmanager
def use_logging_redirect(add_log_entry_func: Callable[[str], None]):
    """
    Context manager that redirects logging to a context-specific buffer.
    """

    key = get_routing_key(prefix="logging")
    buffer = routing_map.add_buffer(key)
    try:
        yield buffer
    finally:
        routing_map.remove_buffer(key)
        logs = buffer.getvalue()
        if logs:
            add_log_entry_func(logs)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord, **kwargs) -> str:
        try:
            from writer.blueprints import get_current_block
            from writer.core import get_app_process, get_session
            current_block = get_current_block()
            app_process = get_app_process()
            session = get_session()
        except RuntimeError:
            current_block = None
            session = None
            app_process = None

        data: Dict[str, Any] = {
            "severity": record.levelname.upper(),
            "message": super().format(record),
            "logger_name": record.name,
            "process": {
                "name": record.processName
            },
            "timestamp": time(),
        }

        if current_block is not None:
            data["component"] = {
                "id": current_block.component.id,
                "type": current_block.component.type
            }

        if session is not None:
            data["session"] = {
                "id": session.session_id,
            }

        if app_process is not None:
            data["process"]["mode"] = app_process.mode

        if isinstance(record.args, dict):
            data.update(record.args)

        # if record.args[0] is a dict add to the json dict
        if isinstance(record.args, tuple):
            if len(record.args) > 0 and isinstance(record.args[0], dict):
                data.update(record.args[0])

        try:
            data_as_json = json.dumps(data)
            return data_as_json 
        except Exception:
            return '{"unserializable": true}' 


def get_handler(format: str = WRITER_LOG_FORMAT, level: str = WRITER_LOG_LEVEL):
    return {
        "level": level,
        "class": "logging.StreamHandler",
        "formatter": format,
    }


def get_logger(level: str = WRITER_LOG_LEVEL):
    return {
        "handlers": ["basic"],
        "level": level,
        "propagate": False,
    }


LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "text": {
            "format": "%(levelname)s - %(name)s - %(message)s",
        },
        "json": {
            "()": JSONFormatter,
        },
        "user": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "basic": get_handler(),
        "stdout": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json" if WRITER_LOG_FORMAT == "json" else None
        },
        "routing": {
            "()": RoutingHandler,
            "formatter": "user",
        }
    },
    "loggers": {
        "root": get_logger(),
        "writer": get_logger(),
        "app": get_logger(),
        "from_app": get_logger(),
        "kv_storage": get_logger(),
        "vault": get_logger(),
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
