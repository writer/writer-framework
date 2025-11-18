<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import WdsModal from "@/wds/WdsModal.vue";
import type { ModalAction } from "@/wds/WdsModal.vue";
import { computed, inject } from "vue";

const socketTimeout = inject(injectionKeys.socketTimeout)!;

const actions = computed<ModalAction[]>(() => [
	{
		desc: "Prevent session to expire",
		loading: socketTimeout.reconnecting.value,
		fn: () => {
			socketTimeout.preventTasks.value.add("stayAwake");
			socketTimeout.reconnect();
		},
	},
	{
		desc: "Reconnect",
		loading: socketTimeout.reconnecting.value,
		fn: () => {
			socketTimeout.reconnect();
		},
	},
]);

const description = `You’ve been disconnected because you were inactive for ${socketTimeout.timeoutMin} minutes. Click below to reconnect and pick up where you left off.`;
</script>

<template>
	<WdsModal
		v-if="socketTimeout.socketClosed.value"
		title="Session Expired"
		:description
		:actions
	>
	</WdsModal>
</template>
