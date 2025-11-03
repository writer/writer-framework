<script setup lang="ts">
import { useWriterTracking } from "@/composables/useWriterTracking";
import injectionKeys from "@/injectionKeys";
import WdsModal from "@/wds/WdsModal.vue";
import type { ModalAction } from "@/wds/WdsModal.vue";
import { ref, onMounted, onUnmounted, inject } from "vue";

const wf = inject(injectionKeys.core);

const tracking = useWriterTracking(wf);

let timer = undefined;

const SOCKET_TIMEOUT_MIN = 10;
const SOCKET_TIMEOUT_MS = SOCKET_TIMEOUT_MIN * 60 * 1_000;

const socketClosed = ref(false);

function scheduleSocketClose() {
	if (timer) clearTimeout(timer);
	timer = setTimeout(() => {
		wf.stopSync();
		socketClosed.value = true;
	}, SOCKET_TIMEOUT_MS);
}

let clearRegisterTrackCallback: () => void | undefined;

const actions: ModalAction[] = [
	{
		desc: "Reconnect",
		fn: () => {
			window.location.reload();
		},
	},
];

const description = `You’ve been disconnected because you were inactive for ${SOCKET_TIMEOUT_MIN} minutes. Click below to reconnect and pick up where you left off.`;

onMounted(() => {
	scheduleSocketClose();
	clearRegisterTrackCallback =
		tracking.registerTrackCallback(scheduleSocketClose);
});

onUnmounted(() => {
	if (timer) clearTimeout(timer);
	if (clearRegisterTrackCallback) clearRegisterTrackCallback();
});
</script>

<template>
	<WdsModal v-if="socketClosed" title="Session Expired" :description :actions>
	</WdsModal>
</template>
