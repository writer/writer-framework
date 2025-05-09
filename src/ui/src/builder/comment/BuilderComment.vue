<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { inject, computed, CSSProperties } from "vue";
import BuilderCommentNew from "./BuilderCommentNew.vue";

const props = defineProps({
	componentId: { type: String, required: true },
});
const wf = inject(injectionKeys.core);

const component = computed(() => wf.getComponentById(props.componentId));

function numbertoPx(value: number | undefined) {
	return typeof value === "number" ? `${value}px` : undefined;
}

const style = computed<CSSProperties>(() => ({
	top: numbertoPx(component.value?.x),
	left: numbertoPx(component.value?.y),
}));
</script>

<template>
	<button type="button" :style="style" class="BuilderComment">
		<BuilderCommentNew />
	</button>
</template>

<style lang="css" scoped>
.BuilderComment {
	position: absolute;
	cursor: pointer;

	background-color: transparent;
	border: none;
}
</style>
