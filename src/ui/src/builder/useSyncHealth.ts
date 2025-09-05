import type { WdsStateDotState } from "@/wds/WdsStateDot.vue";
import type { Core } from "@/writerTypes";
import { computed, watch } from "vue";
import { Toast, useToasts } from "./useToast";

export function useSyncHealth(wf: Core) {
	const toastManager = useToasts();

	let activeToastId: Toast["id"] | undefined = undefined;

	function displayToast(toast: Omit<Toast, "id">) {
		if (activeToastId) {
			toastManager.pushToast({ id: activeToastId, ...toast });
		} else {
			activeToastId = toastManager.pushToast(toast);
		}
	}

	watch(wf.syncHealth, (syncHealth, previousSyncHealth) => {
		switch (syncHealth) {
			case "idle":
				return displayToast({
					type: "loading",
					message: "Connecting to the server",
					closable: false,
					delayMs: Infinity,
				});
			case "connected":
				return displayToast({
					message:
						previousSyncHealth === "suspended"
							? "The server has restarted"
							: "The connection to the server has been restored.",
					type: "success",
				});
			case "offline":
				return displayToast({
					type: "loading",
					message:
						"Connection was lost due to a network issue or an ongoing update. Please hang tight!",
					closable: false,
					delayMs: Infinity,
				});
			case "suspended":
				return displayToast({
					message: "Restarting the server...",
					type: "loading",
					closable: false,
					delayMs: Infinity,
				});
		}
	});

	const syncHealthStatus = computed(() => {
		let s = "";
		switch (wf.syncHealth.value) {
			case "offline":
				s += "Offline. Not syncing.";
				break;
			case "connected":
				s += "Online. Syncing...";
				break;
			case "idle":
				s += "Sync not initialised.";
				break;
			case "suspended":
				s += "Sync suspended.";
				break;
		}

		if (wf.featureFlags.value.length > 0) {
			s += ` Feature flags: ${wf.featureFlags.value.join(", ")}`;
		}

		return s;
	});

	const stateDotState = computed<WdsStateDotState>(() => {
		switch (wf.syncHealth.value) {
			case "offline":
			case "suspended":
			case "idle":
				return "error";
			default:
				return "deployed";
		}
	});

	return { syncHealthStatus, stateDotState };
}
