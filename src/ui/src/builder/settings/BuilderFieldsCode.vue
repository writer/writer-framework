<template>
	<BuilderEmbeddedCodeEditor
		v-model="code"
		language="python"
		:variant="isExpanded ? 'full' : 'minimal'"
		class="BuilderFieldsCode"
		:class="{ 'BuilderFieldsCode--expanded': isExpanded }"
	>
	</BuilderEmbeddedCodeEditor>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, PropType, ref, watch } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import { Component } from "@/writerTypes";
import BuilderEmbeddedCodeEditor from "../BuilderEmbeddedCodeEditor.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
	isExpanded: { type: Boolean, required: true },
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

.BuilderFieldsCode--expanded {
	min-height: 300px;
}
</style>
