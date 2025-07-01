<script setup lang="ts">
import { nextTick, onMounted, useTemplateRef, watch } from "vue";
import BaseMarkdown from "../../base/BaseMarkdown.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";

const props = defineProps({
	value: { validator: () => true, required: true },
	useMarkdown: { type: Boolean, required: false },
	editable: { type: Boolean, required: false },
	wrapText: { type: Boolean, required: false },
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

function autoResizeFromRef() {
	if (!textarea.value?.ref) return;

	const el = textarea.value.ref as HTMLTextAreaElement;

	const style = getComputedStyle(el);
	if (!style) return;

	el.style.height = "auto";

	const borderTop = parseFloat(style.borderTopWidth || "0");
	const borderBottom = parseFloat(style.borderBottomWidth || "0");
	const verticalBorder = borderTop + borderBottom;

	el.style.height = `${el.scrollHeight + verticalBorder}px`;
}

onMounted(() => {
	if (props.wrapText && props.editable) {
		nextTick(() => autoResizeFromRef());
	}
});

watch(
	() => props.editable || props.value,
	() => {
		if (props.wrapText && props.editable) {
			nextTick(() => autoResizeFromRef());
		}
	},
);
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
		<p :class="{ 'CoreDataframeCellText__content--noWrap': !wrapText }">
			{{ value }}
		</p>
	</div>
</template>

<style scoped>
.CoreDataframeCellText--textarea,
.CoreDataframeCellText--text {
	width: 100%;
	font-size: inherit;
	overflow: hidden;
	white-space: pre-wrap;
	word-wrap: break-word;
	overflow-wrap: break-word;
	word-break: break-word;
}

.CoreDataframeCellText--text {
	padding: 8.5px 12px 8.5px 12px;
	border: 1px solid transparent;

	width: 100%;
}
.CoreDataframeCellText__content--noWrap {
	text-overflow: ellipsis;
	white-space: nowrap;
}

.CoreDataframeCellText--textarea {
	resize: vertical;
	height: 100%;
}
</style>
