import { useAbortController } from "@/composables/useAbortController";
import type { Core } from "@/writerTypes";
import { ref, onMounted, watch } from "vue";

/**
 * @param timeoutMin the inactivity time required to close the socket
 */
export function useSocketTimeout(wf: Core, timeoutMin: number) {
	const timeoutMs = timeoutMin * 60 * 1_000;

	let timer = undefined;

	const socketClosed = ref(false);
	const reconnecting = ref(false);
	const prevent = ref(false);

	function schedule() {
		if (document.visibilityState === "visible") return;
		clearSchedule();
		timer = setTimeout(() => {
			wf.stopSync();
			socketClosed.value = true;
		}, timeoutMs);
	}

	function clearSchedule() {
		if (timer) clearTimeout(timer);
	}

	watch(prevent, () => {
		if (prevent.value) clearSchedule();
	});

	async function reconnect() {
		reconnecting.value = true;
		try {
			await wf.init();
			socketClosed.value = false;
		} catch {
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
