import { useAbortController } from "@/composables/useAbortController";
import { useLogger } from "@/composables/useLogger";
import type { Core } from "@/writerTypes";
import { ref, onMounted, watch } from "vue";

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

	function schedule() {
		if (document.visibilityState === "visible") return;
		clearSchedule();
		timer = setTimeout(() => {
			logger.warn(`[SocketTimeout] Closing socket after ${timeoutMin} minutes of inactivity (tab hidden)`);
			wf.stopSync();
			socketClosed.value = true;
			logger.info(`[SocketTimeout] Socket closed`);
		}, timeoutMs);
	}

	function clearSchedule() {
		if (timer) clearTimeout(timer);
	}

	watch(prevent, () => {
		if (prevent.value) clearSchedule();
	});

	async function reconnect() {
		logger.info(`[SocketTimeout] Attempting to reconnect socket...`);
		reconnecting.value = true;
		try {
			await wf.init();
			socketClosed.value = false;
			logger.info(`[SocketTimeout] Socket reconnected successfully`);
		} catch (error) {
			logger.error(`[SocketTimeout] Failed to reconnect socket, reloading page`, error);
			window.location.reload(); // fallback to full reload
		} finally {
			reconnecting.value = false;
		}
	}

	const abort = useAbortController();

	onMounted(() => {
		document.addEventListener(
			"visibilitychange",
			() => {
				if (document.visibilityState === "visible") {
					clearSchedule();
				} else if (!prevent.value) {
					schedule();
				}
			},
			{ signal: abort.signal },
		);
	});

	return {
		timeoutMin,
		socketClosed,
		reconnecting,
		prevent,
		clearSchedule,
		schedule,
		reconnect,
	};
}
