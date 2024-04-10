<template>
	<div class="BuilderFieldsText" :data-key="props.fieldKey">
		<template
			v-if="
				!templateField.control ||
				templateField.control == FieldControl.Text
			"
		>
			<BuilderTemplateInput
				class="content"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				:options="templateField.options"
				@input="handleInput"
			/>
		</template>
		<template v-else-if="templateField.control == FieldControl.Textarea">
			<BuilderTemplateTextarea
				class="content"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				@input="handleInput"
			/>
		</template>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, ref, watch } from "vue";
import { Component, FieldControl } from "../streamsyncTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import BuilderTemplateTextarea from "./BuilderTemplateTextarea.vue";
import Fuse from 'fuse.js';

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const autocompleteOptions = ref<string[]>([]);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));
const value = computed(() => component.value.content[fieldKey.value]);
const templateField = computed(() => {
	const { type } = component.value;
	const definition = ss.getComponentDefinition(type);
	return definition.fields[fieldKey.value];
});

const options = computed(() => {
	const field = templateField.value;
	if (field.options) {
		return typeof field.options === "function"
			? field.options(ss, componentId.value)
			: field.options;
	}
	return [];
});

const handleInput = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};

</script>

<style>
.BuilderFieldsText .content {
	padding: 16px 12px 12px 12px;
	width: 100%;
}
</style>

<style scoped>
@import "./sharedStyles.css";

.field-state-autocomplete {
	position: absolute;
	background-color: var(--builderBackgroundColor);
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 4px;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	max-height: 200px;
	overflow-y: auto;
	width: 100%;
	z-index: 2;
}

.field-state-autocomplete-option {
	padding: 8px 12px;
	cursor: pointer;
}

.field-state-autocomplete-option:hover {
	background-color: var(--builderSubtleHighlightColorSolid);
}

textarea {
	resize: vertical;
}
</style>
