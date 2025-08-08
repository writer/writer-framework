<template>
	<BuilderEmbeddedCodeEditor
		v-model="fieldViewModel"
		:language="inputLanguage"
		:variant="isExpanded ? 'half-screen' : 'minimal'"
		class="BuilderFieldsCode"
	>
	</BuilderEmbeddedCodeEditor>
</template>

<script setup lang="ts">
import { PropType, toRef } from "vue";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import { Component } from "@/writerTypes";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BuilderEmbeddedCodeEditor = defineAsyncComponentWithLoader({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
});

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

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
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
