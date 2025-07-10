<script lang="ts" setup>
import { computed, CSSProperties, PropType, useTemplateRef } from "vue";

const props = defineProps({
	tag: { type: String, required: false, default: undefined },
	backgroundColors: {
		type: Object as PropType<Record<string, Set<string>>>,
		required: false,
		default: () => {},
	},
});

const style = computed<CSSProperties>(() => {
	const type = Object.entries(props.backgroundColors ?? {}).find(([, v]) =>
		v.has(props.tag),
	)?.[0];

	if (!type) return {};

	return {
		backgroundColor: type,
	};
});

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
	<span ref="root" class="StateWithPillTag" :style @dblclick="onDblClick">
		<span class="StateWithPillTag__sign">@</span
		><span class="StateWithPillTag__bracket">{</span>{{ tag
		}}<span class="StateWithPillTag__bracket">}</span></span
	>
</template>

<style lang="css" scoped>
.StateWithPillTag {
	display: inline-block;
	background-color: var(--wdsColorGray0);
	color: var(--wdsColorBlack);
	padding: 2px 8px;
	border-radius: 4px;
}
.StateWithPillTag::selection {
	background: var(--builderSelectedColor);
}

.StateWithPillTag__bracket {
	color: transparent;
	caret-color: var(--wdsColorBlack);
	display: inline-block;
	width: 0;
}
</style>
