import type { WdsStateDotState } from "@/wds/WdsStateDot.vue";
import type { Core } from "@/writerTypes";
import { computed, shallowRef, watch } from "vue";
import { useToasts } from "./useToast";

type AlertModal = { title: string; description: string };

export function useSyncHealth(wf: Core) {
	const alertModal = shallowRef<AlertModal | undefined>();
	const toast = useToasts();

	let restartingToast: number | undefined = undefined;

	let syncHealthTimer: ReturnType<typeof setTimeout>;

	function displayAlertModal(ms: number) {
		if (syncHealthTimer) clearTimeout(syncHealthTimer);

		syncHealthTimer = setTimeout(() => {
			alertModal.value = {
				title: "We’re trying to reconnect...",
				description:
					"Connection was lost due to a network issue or an ongoing update. Please hang tight!",
			};
		}, ms);
	}

	function closeAlertModal() {
		if (alertModal.value) alertModal.value = undefined;
		if (syncHealthTimer) clearTimeout(syncHealthTimer);
	}

	watch(wf.syncHealth, (syncHealth, prevSyncHealth) => {
		if (syncHealth === "offline") {
			return displayAlertModal(1_000);
		}
		closeAlertModal();

		if (prevSyncHealth === "connected" && syncHealth === "suspended") {
			displayAlertModal(10_000);
			restartingToast = toast.pushToast({
				message: "Restarting the server...",
				type: "loading",
				closable: false,
				delayMs: Infinity,
			});
		}

		if (prevSyncHealth === "suspended" && syncHealth === "connected") {
			if (restartingToast) {
				toast.updateToast({
					id: restartingToast,
					message: "Server restarted successfully",
					type: "info",
				});
			} else {
				toast.pushToast({
					message: "Server restarted successfully",
					type: "info",
				});
			}
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

	return { alertModal, syncHealthStatus, stateDotState };
}
