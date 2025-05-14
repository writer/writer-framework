import type { Core, UserCollaborationPing } from "@/writerTypes";
import { ref, Ref } from "vue";

const outgoingPing: Ref<Partial<UserCollaborationPing>> = ref({});
export const userCollaborationProfile: UserCollaborationPing["profile"] = {
	userId: null,
	name: "Unknown",
};
let pingTimer: ReturnType<typeof setTimeout> | null = null;
let snapshotGroomingTimer: ReturnType<typeof setTimeout> | null = null;

const PING_INTERVAL_MS = 1000;
const SNAPSHOT_GROOMING_INTERVAL_MS = 1000;

export const collaborationSnapshot = ref({});

export function handleIncomingCollaborationUpdate(
	incomingPing: UserCollaborationPing,
) {
	const incomingUserId = incomingPing.profile.userId;
	if (typeof incomingUserId == "undefined") return;
	collaborationSnapshot.value = {
		...collaborationSnapshot.value,
		[incomingUserId]: incomingPing,
	};
}

export function useCollaboration(wf: Core) {
	function groomSnapshot() {
		clearTimeout(snapshotGroomingTimer);
		snapshotGroomingTimer = setTimeout(
			groomSnapshot,
			SNAPSHOT_GROOMING_INTERVAL_MS,
		);
	}

	function updateOutgoingPing(ping: Partial<UserCollaborationPing>) {
		outgoingPing.value = { ...outgoingPing.value, ...ping };
	}

	function sendCollaborationPing() {
		wf.sendCollaborationPing({
			profile: userCollaborationProfile,
			action: "auto",
			time: new Date(),
			...outgoingPing.value,
		});
		outgoingPing.value.action = "auto";
		clearTimeout(pingTimer);
		pingTimer = setTimeout(sendCollaborationPing, PING_INTERVAL_MS);
	}

	return { groomSnapshot, updateOutgoingPing, sendCollaborationPing };
}
