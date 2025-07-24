<script lang="ts" setup>
import { computed, CSSProperties, PropType, useTemplateRef } from "vue";

const props = defineProps({
	tag: { type: String, required: false, default: undefined },
	backgroundColors: {
		type: Object as PropType<Record<string, string[]>>,
		required: false,
		default: () => {},
	},
});

const style = computed<CSSProperties>(() => {
	const type = Object.entries(props.backgroundColors ?? {}).find(([, keys]) =>
		keys.some((k) => props.tag === k || props.tag.startsWith(`${k}.`)),
	)?.[0];

	if (!type) return {};

	return {
		backgroundColor: type,
	};
});

const content = computed(() => `@{${props.tag}}`);

const root = useTemplateRef("root");

function onDblClick() {
	if (!root.value) return;
	const selection = window.getSelection();
	const range = document.createRange();
	range.selectNodeContents(root.value);
	selection.removeAllRanges();
	selection.addRange(range);
}
</script>

<template>
	<span
		ref="root"
		class="BuilderTemplateEditorContentTag"
		:style
		@dblclick="onDblClick"
	>
		{{ content }}
	</span>
</template>

<style lang="css" scoped>
.BuilderTemplateEditorContentTag {
	background-color: var(--wdsColorGray0);
	color: var(--wdsColorBlack);
	padding: 2px 8px;
	border-radius: 4px;
}
</style>
