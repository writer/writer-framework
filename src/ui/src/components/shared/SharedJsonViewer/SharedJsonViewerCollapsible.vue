<template>
	<SharedCollapsible
		:open="open"
		:disabled="disabled"
		:icons="{ close: 'keyboard_arrow_right', open: 'keyboard_arrow_down' }"
		@toggle="$emit('toggle', $event)"
	>
		<template #title>
			<div class="SharedJsonViewerCollapsible__title">
				<span v-if="title">{{ title }}</span>
				<SharedJsonViewerChildrenCounter v-if="data" :data="data" />
			</div>
		</template>
		<template #content>
			<div class="SharedJsonViewerCollapsible__content">
				<slot />
			</div>
		</template>
	</SharedCollapsible>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import SharedCollapsible from "../SharedCollapsible.vue";
import type { JsonData } from "./SharedJsonViewer.vue";
import SharedJsonViewerChildrenCounter from "./SharedJsonViewerChildrenCounter.vue";

defineProps({
	open: { type: Boolean, required: false },
	disabled: { type: Boolean, required: false },
	title: { type: String, required: false, default: undefined },
	data: {
		type: [
			String,
			Number,
			Boolean,
			Object,
			Array,
			null,
		] as PropType<JsonData>,
		required: false,
		default: undefined,
	},
});

defineEmits({
	toggle: (open: boolean) => typeof open === "boolean",
});
</script>

<style scoped>
.SharedJsonViewerCollapsible__title {
	font-family: monospace;
	font-size: 12px;
	display: flex;
	gap: 8px;
}

.SharedJsonViewerCollapsible__content {
	margin-left: 7px;
	padding-left: var(--jsonViewerIndentationSpacing, 8px);
	padding-top: 4px;
	padding-bottom: 4px;
}
</style>
