/**
 * Language Server Protocol (LSP) client for Python language support.
 *
 * This module manages the WebSocket connection to the python-lsp-server (pylsp)
 * and integrates it with Monaco editor for enhanced Python language features.
 */

import {
	WebSocketMessageReader,
	WebSocketMessageWriter,
	toSocket,
} from "vscode-ws-jsonrpc";
import { CloseAction, ErrorAction } from "vscode-languageclient/browser.js";
import { MonacoLanguageClient } from "monaco-languageclient";
import { useLogger } from "../composables/useLogger.js";

const logger = useLogger();

interface LSPConfig {
	enabled: boolean;
	port: number | null;
	host: string | null;
}

let languageClient: MonacoLanguageClient | null = null;
let webSocket: WebSocket | null = null;

/**
 * Constructs the WebSocket URL for the LSP server.
 * Uses the same pattern as the main WebSocket connection in core/index.ts.
 *
 * @param port - The port the LSP server is running on
 * @returns WebSocket URL
 */
function constructWebSocketURL(port: number): string {
	// Use relative URL construction like the main WebSocket
	const url = new URL(window.location.href);
	url.protocol = url.protocol.replace("https", "wss");
	url.protocol = url.protocol.replace("http", "ws");
	url.port = port.toString();
	url.pathname = "/"; // LSP server is at the root
	url.hash = ""; // Remove fragment identifier (WebSocket doesn't allow it)
	url.search = ""; // Remove query string
	return url.href;
}

/**
 * Fetches the LSP configuration from the backend API.
 *
 * @returns LSP configuration or null if fetch fails
 */
async function fetchLSPConfig(): Promise<LSPConfig | null> {
	try {
		const response = await fetch("/api/lsp-config");
		if (!response.ok) {
			logger.warn("LSP config endpoint not available:", response.status);
			return null;
		}
		const config: LSPConfig = await response.json();
		return config;
	} catch (error) {
		logger.error("Failed to fetch LSP config:", error);
		return null;
	}
}

/**
 * Creates a Monaco Language Client instance.
 *
 * @param reader - WebSocket message reader
 * @param writer - WebSocket message writer
 * @returns Configured MonacoLanguageClient
 */
function createLanguageClient(
	reader: WebSocketMessageReader,
	writer: WebSocketMessageWriter,
): MonacoLanguageClient {
	const client = new MonacoLanguageClient({
		name: "Python Language Client",
		clientOptions: {
			// Document selector for Python files
			documentSelector: [
				{ language: "python" },
				{ scheme: "inmemory", language: "python" },
				{ pattern: "**/*.py" },
			],
			// Disable default error handler to prevent client restart loops
			errorHandler: {
				error: () => ({ action: ErrorAction.Continue }),
				closed: () => ({ action: CloseAction.DoNotRestart }),
			},
			// Synchronize settings with server
			synchronize: {
				fileEvents: [],
			},
			// Initialize options passed to the server
			initializationOptions: {},
		},
		// Provide message transports directly (v10+ API)
		messageTransports: { reader, writer },
	});

	return client;
}

/**
 * Initializes the WebSocket connection and starts the language client.
 *
 * @param url - WebSocket URL for the LSP server
 * @returns WebSocket instance or null if connection fails
 */
function initWebSocketAndStartClient(url: string): WebSocket | null {
	try {
		const ws = new WebSocket(url);

		ws.onopen = () => {
			logger.log("Python LSP client connected");

			// Create message transports
			const socket = toSocket(ws);
			const reader = new WebSocketMessageReader(socket);
			const writer = new WebSocketMessageWriter(socket);

			// Create and start language client
			const client = createLanguageClient(reader, writer);

			languageClient = client;

			// Start the client and wait for it to be ready
			client
				.start()
				.then(() => {
					logger.log("Python LSP client ready");
				})
				.catch((error) => {
					logger.error("Failed to start LSP client:", error);
				});

			// Stop client when connection closes
			reader.onClose(() => {
				client.stop();
			});
		};

		ws.onerror = (error) => {
			logger.error("LSP WebSocket error:", error);
		};

		ws.onclose = () => {
			if (languageClient) {
				languageClient.stop();
				languageClient = null;
			}
			webSocket = null;
		};

		return ws;
	} catch (error) {
		logger.error("Failed to create LSP WebSocket connection:", error);
		return null;
	}
}

/**
 * Initializes the Python LSP client.
 * This should be called when the application starts in edit mode.
 * Will retry if the server is not ready yet.
 *
 * @param retryCount - Internal retry counter
 * @returns Promise that resolves to true if initialization succeeds, false otherwise
 */
export async function initializeLSPClient(retryCount = 0): Promise<boolean> {
	const MAX_RETRIES = 3;
	const RETRY_DELAY = 1000; // 1 second

	// Check if already initialized
	if (languageClient !== null) {
		return true;
	}

	// Fetch LSP configuration
	const config = await fetchLSPConfig();

	if (!config || !config.enabled || !config.port) {
		if (retryCount < MAX_RETRIES) {
			logger.log(
				`LSP server not ready, retrying (${retryCount + 1}/${MAX_RETRIES})...`,
			);
			await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
			return initializeLSPClient(retryCount + 1);
		}
		return false;
	}

	logger.log("Initializing Python LSP client...");

	// Construct WebSocket URL using current host
	const websocketUrl = constructWebSocketURL(config.port);

	// Initialize WebSocket connection
	webSocket = initWebSocketAndStartClient(websocketUrl);

	return webSocket !== null;
}

/**
 * Checks if the LSP client is currently active.
 *
 * @returns True if LSP client is running, false otherwise
 */
export function isLSPClientActive(): boolean {
	return (
		languageClient !== null &&
		webSocket !== null &&
		webSocket.readyState === WebSocket.OPEN
	);
}

/**
 * Gets the active language client instance.
 * Used for manual document synchronization.
 *
 * @returns The active MonacoLanguageClient or null
 */
export function getLSPClient(): MonacoLanguageClient | null {
	return languageClient;
}

/**
 * Stops the LSP client and closes the WebSocket connection.
 * This should be called when the application is shutting down or switching modes.
 */
export function stopLSPClient(): void {
	if (languageClient) {
		languageClient.stop();
		languageClient = null;
	}

	if (webSocket) {
		webSocket.close();
		webSocket = null;
	}
}
