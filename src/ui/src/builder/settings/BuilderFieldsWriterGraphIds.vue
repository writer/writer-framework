<template>
	<div
		class="BuilderFieldsWriterGraphIds"
		:data-automation-key="props.fieldKey"
	>
		<BuilderGraphSelect
			ref="selectorEl"
			v-model="selected"
			enable-multi-selection
		/>
	</div>
</template>

<script setup lang="ts">
import {
	toRefs,
	inject,
	computed,
	defineAsyncComponent,
	useTemplateRef,
} from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";

const BuilderGraphSelect = defineAsyncComponent(
	() => import("../BuilderGraphSelect.vue"),
);

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
});
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const selectorEl = useTemplateRef("selectorEl");

const fieldDefinition = computed(() => {
	const def = wf.getComponentDefinition(component.value.type);
	return def?.fields?.[props.fieldKey];
});

const selected = computed<string[]>({
	get() {
		const raw =
			component.value.content[props.fieldKey] ??
			fieldDefinition.value?.default ??
			"[]";
		try {
			return JSON.parse(raw);
		} catch {
			return [];
		}
	},
	set(value) {
		setContentValue(
			component.value.id,
			fieldKey.value,
			JSON.stringify(value),
		);
	},
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsWriterGraphIds {
	display: grid;
	grid-template-columns: minmax(0, 1fr);
	align-items: center;
	gap: 12px;
}
</style>
