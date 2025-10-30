<template>
	<WdsModal
		title="Unsaved Changes"
		description="You have unsaved changes. What would you like to do?"
		:actions="modalActions"
		display-close-button
		@close="emits('cancel')"
	>
		<div class="UnsavedChangesModal__content">
			<div class="UnsavedChangesModal__icon">
				<WdsIcon name="alert-triangle" />
			</div>
			<div class="UnsavedChangesModal__message">
				<p>
					The file <strong>{{ filename }}</strong> has unsaved
					changes.
				</p>
				<p>Your changes will be lost if you don't save them.</p>
			</div>
		</div>
	</WdsModal>
</template>

<script setup lang="ts">
import { computed } from "vue";
import WdsModal, { type ModalAction } from "@/wds/WdsModal.vue";
import WdsIcon from "@/wds/WdsIcon.vue";

const props = defineProps({
	filename: { type: String, required: true },
	isSaving: { type: Boolean, required: false },
});

const emits = defineEmits({
	save: () => true,
	cancel: () => true,
});

const modalActions = computed<ModalAction[]>(() => [
	{
		desc: "Cancel",
		fn: () => emits("cancel"),
	},
	{
		desc: "Save",
		fn: () => emits("save"),
		disabled: props.isSaving,
	},
]);
</script>

<style scoped>
.UnsavedChangesModal__content {
	display: flex;
	align-items: flex-start;
	gap: 16px;
	padding: 16px 0;
}

.UnsavedChangesModal__icon {
	flex-shrink: 0;
	width: 48px;
	height: 48px;
	background-color: var(--wdsColorOrange1);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--wdsColorOrange6);
	font-size: 24px;
}

.UnsavedChangesModal__message {
	flex: 1;
}

.UnsavedChangesModal__message p {
	margin: 0 0 8px 0;
	color: var(--primaryTextColor);
	line-height: 1.5;
}

.UnsavedChangesModal__message p:last-child {
	margin-bottom: 0;
	color: var(--secondaryTextColor);
	font-size: 14px;
}
</style>
