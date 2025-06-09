<template>
	<BuilderEmbeddedCodeEditor
		v-model="code"
		:language="inputLanguage"
		:variant="isExpanded ? 'full' : 'minimal'"
		class="BuilderFieldsCode"
	>
	</BuilderEmbeddedCodeEditor>
</template>

<script setup lang="ts">
import {
	toRefs,
	inject,
	computed,
	PropType,
	ref,
	watch,
	defineAsyncComponent,
} from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";

const BuilderEmbeddedCodeEditor = defineAsyncComponent({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
	isExpanded: { type: Boolean, required: true },
	inputLanguage: {
		type: String as PropType<"python" | "json">,
		required: true,
	},
});
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));
const code = ref(component.value.content[fieldKey.value]);

watch(code, (newCode) => {
	setContentValue(component.value.id, fieldKey.value, newCode);
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsCode {
	font-size: inherit;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	overflow: hidden;
}
</style>
