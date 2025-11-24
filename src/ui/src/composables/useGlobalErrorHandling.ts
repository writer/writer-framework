import { trackError } from "@/observability/frontendMetrics";

let isInitialized = false;
let errorHandlerRef: ((event: ErrorEvent) => void) | null = null;
let rejectionHandlerRef: ((event: PromiseRejectionEvent) => void) | null = null;

function extractError(error: unknown): Error {
	if (error instanceof Error) {
		return error;
	}
	if (typeof error === "string") {
		return new Error(error);
	}
	return new Error(String(error || "Unknown error"));
}

function handleError(event: ErrorEvent): void {
	try {
		const error = extractError(event.error || event.message);
		trackError(error, error.name || "window_error");
	} catch (trackingError) {
		console.error("Failed to track error:", trackingError);
	}
}

function handleUnhandledRejection(event: PromiseRejectionEvent): void {
	try {
		const error = extractError(event.reason);
		trackError(error, "unhandled_promise_rejection");
	} catch (trackingError) {
		console.error("Failed to track promise rejection:", trackingError);
	}
}

export function setupGlobalErrorHandling(): void {
	if (typeof window === "undefined") {
		return;
	}

	if (isInitialized) {
		console.warn("Global error handling already initialized");
		return;
	}

	errorHandlerRef = handleError;
	rejectionHandlerRef = handleUnhandledRejection;

	window.addEventListener("error", errorHandlerRef);
	window.addEventListener("unhandledrejection", rejectionHandlerRef);

	isInitialized = true;
}

export function teardownGlobalErrorHandling(): void {
	if (typeof window === "undefined" || !isInitialized) {
		return;
	}

	if (errorHandlerRef) {
		window.removeEventListener("error", errorHandlerRef);
		errorHandlerRef = null;
	}

	if (rejectionHandlerRef) {
		window.removeEventListener("unhandledrejection", rejectionHandlerRef);
		rejectionHandlerRef = null;
	}

	isInitialized = false;
}
