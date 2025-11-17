import { useAbortController } from "@/composables/useAbortController";
import { useLogger } from "@/composables/useLogger";
import type { Core } from "@/writerTypes";
import { ref, onMounted, watch, computed } from "vue";

const WEBSOCKET_INACTIVITY_CLOSE_CODE = 4000;

/**
 * @param timeoutMin the inactivity time required to close the socket
 */
export function useSocketTimeout(wf: Core, timeoutMin: number) {
	const timeoutMs = timeoutMin * 60 * 1_000;
	const logger = useLogger();

	let timer = undefined;

	const socketClosed = ref(false);
	const reconnecting = ref(false);
	const prevent = ref(false);

	const ignoreMessageType = new Set([
		"collaborationPing",
		"listResources",
		"keepAlive",
	]);

	const isMessagePending = computed(() => {
		for (const a of wf.frontendMessageMap.value.values()) {
			if (!ignoreMessageType.has(a.type)) return true;
		}
		return false;
	});

	const canCloseSocket = computed(
		() => !prevent.value && !isMessagePending.value,
	);

	const abort = useAbortController();

	function schedule() {
		if (!canCloseSocket.value || document.visibilityState !== "hidden")
			return false;
		clearSchedule();
		logger.log(`[SocketTimeout] planning timeout in ${timeoutMin}min`);
		timer = setTimeout(() => {
			if (!canCloseSocket.value) return;
			logger.warn(
				`[SocketTimeout] Closing socket after ${timeoutMin} minutes of inactivity (tab hidden)`,
			);
			wf.stopSync(WEBSOCKET_INACTIVITY_CLOSE_CODE);
			socketClosed.value = true;
			logger.info(`[SocketTimeout] Socket closed`);
		}, timeoutMs);
		return true;
	}

	function clearSchedule() {
		if (!timer) return;
		logger.log(`[SocketTimeout] canceling timeout `);
		clearTimeout(timer);
		timer = undefined;
	}

	watch(canCloseSocket, () => {
		if (!canCloseSocket.value) {
			clearSchedule();
		} else if (document.visibilityState === "hidden") {
			schedule(); // Reschedule now that activity is complete
		}
	});

	async function reconnect() {
		logger.info(`[SocketTimeout] Attempting to reconnect socket...`);
		reconnecting.value = true;
		try {
			await wf.init();
			socketClosed.value = false;
			logger.info(`[SocketTimeout] Socket reconnected successfully`);
		} catch (error) {
			logger.error(
				`[SocketTimeout] Failed to reconnect socket, reloading page`,
				error,
			);
			window.location.reload(); // fallback to full reload
		} finally {
			reconnecting.value = false;
		}
	}

	function onVisibilityChange() {
		if (document.visibilityState === "visible") {
			clearSchedule();
		} else if (canCloseSocket.value) {
			schedule();
		}
	}

	onMounted(() => {
		document.addEventListener("visibilitychange", onVisibilityChange, {
			signal: abort.signal,
		});
	});

	return {
		timeoutMin,
		socketClosed,
		reconnecting,
		prevent,
		onVisibilityChange,
		clearSchedule,
		schedule,
		reconnect,
	};
}
