<template>
	<div class="BuilderFieldsCheckbox" :data-automation-key="props.fieldKey">
		<WdsCheckbox
			v-model="model"
			:label="label"
			:detail="hint"
			:invalid="Boolean(error)"
		/>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, PropType } from "vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import { Component } from "@/writerTypes";
import injectionKeys from "@/injectionKeys";
import { useComponentActions } from "../useComponentActions";

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	label: { type: String, default: undefined },
	hint: { type: String, default: undefined },
	error: { type: String, default: undefined },
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { setContentValue } = useComponentActions(wf, ssbm);

const component = computed(() => wf.getComponentById(props.componentId));

const model = computed<boolean>({
	get: () => component.value.content[props.fieldKey] === "yes",
	set: (checked) => {
		setContentValue(
			component.value.id,
			props.fieldKey,
			checked ? "yes" : "no",
		);
	},
});
</script>

<style scoped>
@import "../sharedStyles.css";
</style>
