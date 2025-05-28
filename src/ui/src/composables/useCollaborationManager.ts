import type { Core, UserCollaborationPing } from "@/writerTypes";
import { computed, ref, Ref } from "vue";
import { useWriterApi } from "@/composables/useWriterApi.js";

const PING_INTERVAL_MS = 2000;
const SNAPSHOT_GROOMING_INTERVAL_MS = 1000;
const MAX_SNAPSHOT_AGE_MS = 5000;

type UserCollaborationProfile = {
	userId: string;
	displayName: string;
	avatar?: string;
	email?: string;
};

export function useCollaborationManager(wf: Core) {
	const outgoingPing: Ref<Partial<UserCollaborationPing>> = ref({});
	let pingTimer: ReturnType<typeof setTimeout> | null = null;
	let snapshotGroomingTimer: ReturnType<typeof setTimeout> | null = null;

	const collaborationSnapshot: Ref<Record<string, UserCollaborationPing>> =
		ref({});
	const userId: Ref<string> = ref(null);
	const profiles: Ref<Record<string, UserCollaborationProfile>> = ref({});
	const connectedProfiles: Ref<UserCollaborationProfile[]> = ref([]);
	const { writerApi } = useWriterApi();

	const connectedProfilesByInstancePath = computed(() => {
		const r: Record<string, UserCollaborationProfile[]> = {};
		connectedProfiles.value.forEach((profile) => {
			const userId = profile.userId;
			const instancePaths =
				collaborationSnapshot.value[userId]?.selection?.map(
					(s) => s.instancePath,
				) ?? [];
			instancePaths.forEach((instancePath) => {
				r[instancePath] = [...(r[instancePath] ?? []), profile];
			});
		});
		return r;
	});

	function handleIncomingCollaborationUpdate(
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

	function resolveDisplayName(
		firstName: string,
		lastName: string,
		email: string,
	) {
		if (firstName || lastName) {
			return `${firstName} ${lastName}`;
		}
		if (email) {
			return email;
		}
		return "Unknown";
	}

	async function getProfile(userId: string) {
		const profile = profiles.value[userId];
		if (profile) {
			return profile;
		}
		const thirdUserProfile = await writerApi.fetchThirdUserProfile(userId);
		const displayName = resolveDisplayName(
			thirdUserProfile.firstName,
			thirdUserProfile.lastName,
			thirdUserProfile.email,
		);
		profiles.value[userId] = {
			userId,
			displayName,
			avatar: thirdUserProfile.avatar,
			email: thirdUserProfile.email,
		};
		return profiles.value[userId];
	}

	async function getConnectedProfiles() {
		const connectedUserIds = Object.keys(collaborationSnapshot.value);
		const connectedProfiles = connectedUserIds.map((userId) =>
			getProfile(userId),
		);
		return Promise.all(connectedProfiles);
	}

	async function groomSnapshot() {
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
		connectedProfiles.value = await getConnectedProfiles();
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

	return {
		groomSnapshot,
		updateOutgoingPing,
		sendCollaborationPing,
		handleIncomingCollaborationUpdate,
		connectedProfiles,
		connectedProfilesByInstancePath,
	};
}
