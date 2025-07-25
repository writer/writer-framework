<template>
	<WdsFieldWrapper
		v-if="isBindingMode"
		is-unbind-button-shown
		:label
		:unit
		:hint
		:error
		:data-automation-key="props.fieldKey"
		@unbind="toggleBindingMode"
	>
		<BuilderFieldsText
			type="state-template"
			:component-id
			:field-key
			:error
		/>
	</WdsFieldWrapper>
	<div
		v-else
		class="BuilderFieldsCheckbox"
		:data-automation-key="props.fieldKey"
	>
		<WdsCheckbox
			v-model="model"
			:label="label"
			:detail="hint"
			:invalid="Boolean(error)"
		/>
		<WdsButton
			size="smallIcon"
			variant="neutral"
			data-writer-tooltip-placement="left"
			data-writer-tooltip="Bind to a variable"
			@click="toggleBindingMode"
		>
			<WdsIcon name="at-sign" />
		</WdsButton>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, PropType, ref } from "vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import { Component } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { useComponentActions } from "../useComponentActions";
import BuilderFieldsText from "./BuilderFieldsText.vue";

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	label: { type: String, default: undefined },
	unit: { type: String, default: undefined },
	hint: { type: String, default: undefined },
	error: { type: String, default: undefined },
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { setContentValue: _setContentValue } = useComponentActions(wf, ssbm);

const component = computed(() => wf.getComponentById(props.componentId));
const contentValue = computed(() => component.value.content[props.fieldKey]);

function setContentValue(value: string) {
	_setContentValue(component.value.id, props.fieldKey, value);
}

const model = computed<boolean>({
	get: () => contentValue.value === "yes",
	set: (checked) => {
		setContentValue(checked ? "yes" : "no");
	},
});

const isBindingMode = ref<boolean>(
	typeof contentValue.value === "string" &&
		!["yes", "no", ""].includes(contentValue.value),
);

const lastBindingValue = ref("");
const lastCheckboxValue = ref(model.value ? "yes" : "no");

function toggleBindingMode() {
	if (isBindingMode.value) {
		lastBindingValue.value = component.value.content[props.fieldKey];
		setContentValue(lastCheckboxValue.value);
		isBindingMode.value = false;
	} else {
		lastCheckboxValue.value = component.value.content[props.fieldKey];
		setContentValue(lastBindingValue.value);
		isBindingMode.value = true;
	}
}
</script>

<style scoped>
.BuilderFieldsCheckbox {
	display: grid;
	grid-template-columns: 1fr auto;
}
</style>
