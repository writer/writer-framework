<template>
	<WdsFieldWrapper
		v-if="isBindingMode"
		is-binding-button-shown
		:is-binding-enabled="isBindingMode"
		:label
		:unit
		:hint
		:error
		:data-automation-key="props.fieldKey"
		@update:is-binding-enabled="toggleBindingMode"
	>
		<BuilderFieldsText
			type="state-template"
			:component-id
			:field-key
			:error
			default-value=""
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
import { computed, PropType, toRef } from "vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import { Component } from "@/writerTypes";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import { useBindingMode } from "./composables/useBindingMode";
import BuilderFieldsText from "./BuilderFieldsText.vue";

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	defaultValue: { type: String, default: undefined },
	label: { type: String, default: undefined },
	unit: { type: String, default: undefined },
	hint: { type: String, default: undefined },
	error: { type: String, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
	defaultValue: toRef(props, "defaultValue"),
});

const { isBindingMode, toggleBindingMode } = useBindingMode({
	fieldViewModel,
});

const model = computed<boolean>({
	get: () => fieldViewModel.value === "yes",
	set: (checked) => {
		fieldViewModel.value = checked ? "yes" : "no";
	},
});
</script>

<style scoped>
.BuilderFieldsCheckbox {
	display: grid;
	grid-template-columns: 1fr auto;
}
</style>
