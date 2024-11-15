<template>
	<ThoughtProcessSteps
		v-if="Array.isArray(content)"
		:content="content"
		style="margin-left: 12px"
	/>
	<div
		v-else
		class="ThoughtProcessStep"
		:class="{ 'ThoughtProcessStep--pending': pending }"
	>
		{{ content }}
		<CoreChatbotLoader v-if="pending" style="width: auto" />
	</div>
</template>

<script lang="ts" setup>
import { defineAsyncComponent, PropType } from "vue";
import type { Message } from "../CoreChatbotMessage.vue";
import ThoughtProcessSteps from "./ThoughtProcessSteps.vue";

const CoreChatbotLoader = defineAsyncComponent(
	() => import("../CoreChatbotLoader.vue"),
);
defineProps({
	content: {
		type: [String, Array] as PropType<Message["content"]>,
		required: true,
	},
	pending: { type: Boolean },
});
</script>

<style scoped>
.ThoughtProcessStep {
	position: relative;
	padding: 8px 16px;

	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	background-color: var(--containerBackgroundColor);
}

.ThoughtProcessStep--pending {
	display: flex;
	align-items: center;
	gap: 8px;
}
</style>
