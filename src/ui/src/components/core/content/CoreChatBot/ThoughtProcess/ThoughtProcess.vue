<template>
	<ThoughtProcessStep
		v-if="pending"
		:content="String(pendingContent)"
		pending
	/>
	<div v-else class="ThoughtProcess">
		<div>
			<button
				class="ThoughtProcess__toggler"
				:class="{
					'ThoughtProcess__toggler--expanded': isExpanded,
				}"
				@click="isExpanded = !isExpanded"
			>
				<i class="icon material-symbols-outlined" aria-hidden="true">{{
					togglerIcon
				}}</i>
				Though process
			</button>
		</div>
		<ThoughtProcessSteps
			v-show="isExpanded"
			:aria-expanded="isExpanded"
			:content="content"
		/>
	</div>
</template>

<script lang="ts" setup>
import { computed, PropType, ref } from "vue";

import ThoughtProcessStep from "./ThoughtProcessStep.vue";
import ThoughtProcessSteps from "./ThoughtProcessSteps.vue";

import type { Message } from "../CoreChatbotMessage.vue";

const props = defineProps({
	content: {
		type: [String, Array] as PropType<Message["content"]>,
		required: true,
	},
	pending: { type: Boolean },
});

const isExpanded = ref(false);

const togglerIcon = computed(() =>
	isExpanded.value ? "arrow_drop_down" : "arrow_drop_up",
);

function getLastContent(content: Message["content"]): string | undefined {
	if (!Array.isArray(content)) return content;
	const element = content.at(-1);
	return Array.isArray(element) ? getLastContent(element) : element;
}

const pendingContent = computed(() => getLastContent(props.content));
</script>

<style scoped>
.ThoughtProcess__toggler {
	display: flex;
	align-items: center;
	gap: 4px;

	border-radius: 16px;
	border: none;
	height: 24px;
	padding: 0 8px;

	cursor: pointer;
	background-color: transparent;
}
.ThoughtProcess__toggler:hover {
	background-color: var(--separatorColor);
}
.ThoughtProcess__toggler--expanded {
	background-color: var(--separatorColor);
	margin-bottom: 16px;
}
.ThoughtProcess__toggler i {
	font-size: 20px;
}
</style>
