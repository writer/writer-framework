import type { Core, UserCollaborationPing } from "@/writerTypes";
import { computed, ref, Ref } from "vue";

const outgoingPing: Ref<Partial<UserCollaborationPing> | null> = ref(null);
let timer: ReturnType<typeof setTimeout> | null = null;

const PING_INTERVAL_MS = 1000;

export function useCollaboration(wf: Core) {
	function updateOutgoingPing(ping: Partial<UserCollaborationPing>) {
		outgoingPing.value = { ...outgoingPing.value, ...ping };
	}

	function sendUpdate() {
		wf.sendCollaborationPing(outgoingPing.value);
		clearTimeout(timer);
		timer = setTimeout(sendUpdate, PING_INTERVAL_MS);
	}

	return { updateOutgoingPing };
}
