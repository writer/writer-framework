<template>
	<BuilderTemplateInput
		class="BuilderFieldsObject"
		:data-automation-key="props.fieldKey"
		multiline
		variant="code"
		:value="fieldViewModel"
		:placeholder="defaultValue"
		:error="error"
		@input="formatAndSetContentValue"
	/>
</template>

<script setup lang="ts">
import { PropType, toRef } from "vue";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import { Component } from "@/writerTypes";

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	defaultValue: { type: String, required: false, default: undefined },
	error: { type: String, required: false, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
	defaultValue: toRef(props, "defaultValue"),
});

const formatAndSetContentValue = (event: Event) => {
	fieldViewModel.value = (event.target as HTMLInputElement).value;
};
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsObject {
	font-size: inherit;
}
</style>
