<template>
	<div
		v-if="wfbm.isSingleSelectionActive"
		:inert="isReadOnly"
		class="BuilderSettingsBinding"
	>
		<WdsTitle2>Binding</WdsTitle2>
		<WdsFieldWrapper
			class="BuilderSettingsBinding__main"
			label="Link Variable"
			:hint="hint"
		>
			<BuilderTemplateInput
				type="state"
				:value="component.binding?.stateRef"
				:component-id="wfbm.firstSelectedId.value"
				@input="
					(ev: Event) =>
						setBinding((ev.target as HTMLInputElement).value)
				"
			/>
		</WdsFieldWrapper>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, watch } from "vue";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTitle2 from "@/wds/WdsTitle2.vue";
import { parseInstancePathString } from "@/renderer/instancePath";
import { useEvaluator } from "@/renderer/useEvaluator";
import { InstancePath } from "@/writerTypes";

defineProps({
	isReadOnly: { type: Boolean },
});

const hint =
	"Connect the result of this block to a dynamic variable you can use across this agent";

const wf = inject(injectionKeys.core)!;
const wfbm = inject(injectionKeys.builderManager)!;
const secretsManager = inject(injectionKeys.secretsManager)!;
const actions = useComponentActions(wf, wfbm);
const { getEvaluatedFields } = useEvaluator(wf, secretsManager);

const selectedInstancePath = computed<InstancePath>(() =>
	parseInstancePathString(wfbm.firstSelectedItem?.value?.instancePath),
);
const component = computed(() =>
	wf.getComponentById(wfbm.firstSelectedId.value),
);
const evaluatedFields = computed(() =>
	getEvaluatedFields(selectedInstancePath.value),
);

const eventTypeToBind = computed(() => {
	const definition = wf.getComponentDefinition(component.value.type);
	if (!definition) return;

	const events = Object.entries(definition.events).filter(([, event]) => {
		if (!event.bindable) return false;
		if (event.enabled === undefined) return true;
		return event.enabled({ evaluatedFields: evaluatedFields.value });
	});
	const bindableEventTypes = events.map(([eventType]) => eventType);
	return bindableEventTypes[0];
});

function setBinding(value: string) {
	actions.setBinding(
		wfbm.firstSelectedId.value,
		value,
		eventTypeToBind.value,
	);
}

// update the binding `eventType` if it change
watch(eventTypeToBind, () => {
	if (!eventTypeToBind.value) return;

	const binding = component.value?.binding;
	if (!binding?.stateRef) return;

	if (eventTypeToBind.value === binding.eventType) return;

	setBinding(binding.stateRef);
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsBinding {
	padding: 24px;
}

.BuilderSettingsBinding[inert] {
	opacity: 0.7;
}

.BuilderSettingsBinding__main {
	margin-top: 16px;
}
</style>
