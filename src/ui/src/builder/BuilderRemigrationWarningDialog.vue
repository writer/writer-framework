<template>
	<WdsModal
		v-if="isOpen"
		title="Migrate again to update your app"
		size="compact"
		display-close-button
		:actions="actions"
		@close="closeDialog"
	>
		<p class="BuilderRemigrationWarningDialog__body">
			Changes made here won't sync automatically. If you already migrated
			to Agent Builder v2, please migrate again to update your app.
		</p>
	</WdsModal>
</template>

<script setup lang="ts">
import { computed } from "vue";
import WdsModal, { type ModalAction } from "@/wds/WdsModal.vue";

const isOpen = defineModel("isOpen", { type: Boolean, default: false });

const actions = computed<ModalAction[]>(() => [
	{
		desc: "I understand",
		fn: closeDialog,
	},
]);

function closeDialog() {
	isOpen.value = false;
}
</script>

<style scoped>
.BuilderRemigrationWarningDialog__body {
	margin: 0 0 4px;
	color: var(--primaryTextColor);
	font-size: 16px;
	line-height: 1.6;
}
</style>
