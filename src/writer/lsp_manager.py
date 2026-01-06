"""
Language Server Protocol (LSP) manager for Python language support.

This module manages the lifecycle of the python-lsp-server (pylsp) process,
providing WebSocket-based LSP features to the Monaco editor in the frontend.
"""

import logging
import shutil
import socket
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)


class LSPManager:
    """Manages the Python Language Server Protocol server lifecycle."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.port: Optional[int] = None
        self.host: str = "127.0.0.1"

    def _find_available_port(self, start_port: int = 5007, end_port: int = 5099) -> int:
        """
        Find an available port in the given range.

        Args:
            start_port: Starting port to check
            end_port: Ending port to check

        Returns:
            Available port number

        Raises:
            RuntimeError: If no available port is found
        """
        for port in range(start_port, end_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind((self.host, port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"No available port found in range {start_port}-{end_port}")

    def _is_pylsp_available(self) -> bool:
        """Check if pylsp command is available in the system."""
        return shutil.which("pylsp") is not None

    def start(self) -> bool:
        """
        Start the Python LSP server.

        Returns:
            True if server started successfully, False otherwise
        """
        # Check if existing process is still alive
        if self.process is not None and self.process.poll() is None:
            logger.info("LSP server is already running")
            return True

        # Clean up dead process if any
        if self.process is not None:
            logger.info("Cleaning up dead LSP server process")
            self.process = None

        if not self._is_pylsp_available():
            logger.warning(
                "pylsp command not found. Python LSP features will not be available. "
                "Install with: pip install python-lsp-server[all]"
            )
            return False

        try:
            self.port = self._find_available_port()
            logger.info(f"Starting Python LSP server on port {self.port}")

            # Start pylsp with WebSocket support
            # Note: pylsp --ws may exit when client disconnects, this is expected behavior
            self.process = subprocess.Popen(
                ["pylsp", "--ws", "--port", str(self.port), "--host", self.host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info(f"LSP server process started with PID {self.process.pid}")

            # Give the server a moment to start
            time.sleep(0.5)

            # Check if process started successfully
            if self.process.poll() is not None:
                # Process terminated immediately
                _, stderr = self.process.communicate()
                logger.error(f"LSP server failed to start: {stderr}")
                self.process = None
                self.port = None
                return False

            logger.info(f"Python LSP server started successfully on port {self.port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            self.process = None
            self.port = None
            return False

    def stop(self):
        """Stop the Python LSP server."""
        if self.process is None:
            return

        logger.info("Stopping Python LSP server")
        try:
            self.process.terminate()
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("LSP server didn't terminate gracefully, forcing kill")
                self.process.kill()
                self.process.wait()
        except Exception as e:
            logger.error(f"Error stopping LSP server: {e}")
        finally:
            self.process = None
            self.port = None

    def is_running(self) -> bool:
        """Check if the LSP server is running."""
        if self.process is None:
            return False
        poll_result = self.process.poll()
        if poll_result is not None:
            logger.debug(f"LSP server process {self.process.pid} has exited with code {poll_result}")
            return False
        return True

    def get_websocket_url(self) -> Optional[str]:
        """
        Get the WebSocket URL for the LSP server.

        Returns:
            WebSocket URL if server is running, None otherwise
        """
        if self.is_running() and self.port is not None:
            return f"ws://{self.host}:{self.port}"
        return None

    def get_config(self) -> dict:
        """
        Get the LSP server configuration for the frontend.
        Automatically restarts the server if it has stopped.

        Returns:
            Dictionary with LSP configuration.
            Note: websocket_url is set to None - frontend should construct
            the URL using the current host and the provided port.
        """
        # Auto-restart if server has stopped
        if not self.is_running():
            logger.info("LSP server is not running, attempting to restart...")
            self.start()

        return {
            "enabled": self.is_running(),
            "port": self.port,
            "host": self.host,  # For reference, but frontend should use window.location.hostname
        }

