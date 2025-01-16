<script setup lang="ts">
import { useTemplateRef } from "vue";
import BaseMarkdown from "../../base/BaseMarkdown.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";

const props = defineProps({
	value: { validator: () => true, required: true },
	useMarkdown: { type: Boolean, required: false },
	editable: { type: Boolean, required: false },
});

const emits = defineEmits({
	change: (value: string) => typeof value === "string",
});

const textarea = useTemplateRef("textarea");

function stopEditing() {
	const newValue = textarea.value.value;
	if (newValue === props.value) return;
	emits("change", textarea.value.value);
}
</script>

<template>
	<WdsTextareaInput
		v-if="editable"
		ref="textarea"
		class="CoreDataframeCellText--textarea"
		rows="1"
		:model-value="String(value)"
		@focusout="stopEditing"
	/>
	<BaseMarkdown v-else-if="useMarkdown" :raw-text="String(value)" />
	<div v-else class="CoreDataframeCellText--text">
		<p class="CoreDataframeCellText__content">{{ value }}</p>
	</div>
</template>

<style scoped>
.CoreDataframeCellText--textarea,
.CoreDataframeCellText--text {
	width: 100%;
	font-size: inherit;
}

.CoreDataframeCellText--text {
	padding: 8.5px 12px 8.5px 12px;
	border: 1px solid transparent;

	width: 100%;
}
.CoreDataframeCellText__content {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.CoreDataframeCellText--textarea {
	resize: vertical;
	height: 100%;
}
</style>
