import type { Core, UserCollaborationPing } from "@/writerTypes";
import { ref, Ref } from "vue";

const outgoingPing: Ref<Partial<UserCollaborationPing>> = ref({});
let pingTimer: ReturnType<typeof setTimeout> | null = null;
let snapshotGroomingTimer: ReturnType<typeof setTimeout> | null = null;

const PING_INTERVAL_MS = 2000;
const SNAPSHOT_GROOMING_INTERVAL_MS = 1000;
const MAX_SNAPSHOT_AGE_MS = 5000;

export const collaborationSnapshot: Ref<Record<string, UserCollaborationPing>> =
	ref({});
export const userId: Ref<number> = ref(null);

export function handleIncomingCollaborationUpdate(
	incomingPing: UserCollaborationPing,
) {
	const incomingUserId = incomingPing.userId;
	if (typeof incomingUserId == "undefined") return;

	if (incomingPing.action == "leave") {
		delete collaborationSnapshot.value[incomingUserId];
		return;
	}

	collaborationSnapshot.value = {
		...collaborationSnapshot.value,
		[incomingUserId]: incomingPing,
	};
}

export function getProfile() {
	return;
}

export function useCollaboration(wf: Core) {
	function groomSnapshot() {
		clearTimeout(snapshotGroomingTimer);
		const inactiveUsers = [];
		Object.keys(collaborationSnapshot.value).forEach((userId) => {
			const lastUpdate = collaborationSnapshot.value[userId]?.time;
			if (!lastUpdate) return;
			const updateAge = Date.now() - new Date(lastUpdate).getTime();
			if (updateAge > MAX_SNAPSHOT_AGE_MS) {
				inactiveUsers.push(userId);
			}
		});
		inactiveUsers.forEach(
			(userId) => delete collaborationSnapshot.value[userId],
		);
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
			userId: userId.value,
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
