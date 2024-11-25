<template>
	<ul class="ThoughtProcessSteps">
		<li
			v-for="(line, index) of contentAsArray"
			:key="index"
			class="ThoughtProcessSteps__step"
		>
			<ThoughtProcessStep :content="line" />
		</li>
	</ul>
</template>

<script lang="ts" setup>
import { computed, PropType } from "vue";
import type { Message } from "../CoreChatbotMessage.vue";

import ThoughtProcessStep from "./ThoughtProcessStep.vue";

const props = defineProps({
	content: {
		type: [String, Array] as PropType<Message["content"]>,
		required: true,
	},
});

const contentAsArray = computed(() =>
	Array.isArray(props.content) ? props.content : [props.content],
);
</script>

<style scoped>
.ThoughtProcessSteps {
	display: flex;
	gap: 8px;
	flex-direction: column;

	list-style: none;
	position: relative;
}
/* vertical line behind the messages */
.ThoughtProcessSteps::before {
	content: "";
	background-color: var(--separatorColor);
	width: 1px;
	height: 100%;
	position: absolute;
	left: 17px;
}
</style>
