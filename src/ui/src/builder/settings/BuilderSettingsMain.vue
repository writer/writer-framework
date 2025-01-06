<template>
	<div class="BuilderSettingsMain">
		<div v-if="isReadOnly" class="warning cmc-warning">
			<i class="material-symbols-outlined">warning</i>
			<span>
				This component is instantiated in code. All settings in this
				panel are read-only and cannot be edited.
			</span>
		</div>

		<div class="sections" :inert="isReadOnly">
			<BuilderSettingsProperties></BuilderSettingsProperties>
			<template
				v-if="
					!componentDefinition.toolkit ||
					componentDefinition.toolkit == 'core'
				"
			>
				<BuilderSettingsBinding
					v-if="isBindable"
				></BuilderSettingsBinding>
				<BuilderSettingsHandlers></BuilderSettingsHandlers>
				<BuilderSettingsVisibility></BuilderSettingsVisibility>
			</template>
			<BuilderSettingsAPICode>Execute via API</BuilderSettingsAPICode>
		</div>

		<div class="sections debug">
			<div>
				Component id:
				<BuilderCopyText>{{ ssbm.getSelectedId() }}</BuilderCopyText>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, watch, defineAsyncComponent } from "vue";
import injectionKeys from "@/injectionKeys";

import BuilderSettingsProperties from "./BuilderSettingsProperties.vue";
import BuilderSettingsBinding from "./BuilderSettingsBinding.vue";
import BuilderSettingsVisibility from "./BuilderSettingsVisibility.vue";
import BuilderCopyText from "../BuilderCopyText.vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import BuilderSettingsAPICode from "./BuilderSettingsAPICode.vue";

const BuilderSettingsHandlers = defineAsyncComponent({
	loader: () => import("./BuilderSettingsHandlers.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() => wf.getComponentById(ssbm.getSelectedId()));
const isReadOnly = computed(() => component.value.isCodeManaged);

const componentDefinition = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition;
});

watch(component, (newComponent) => {
	if (!newComponent) ssbm.setSelection(null);
});

const isBindable = computed(() =>
	Object.values(componentDefinition.value?.events ?? {}).some(
		(e) => e.bindable,
	),
);
</script>

<style scoped>
@import "../sharedStyles.css";

.sections {
	display: flex;
	flex-direction: column;
}

.sections > * {
	padding: 24px;
}

.sections > *:not(:first-child),
.sections .debug {
	border-top: 1px solid var(--builderSeparatorColor);
}

.sections[inert] {
	opacity: 0.7;
}

.debug {
	color: var(--builderSecondaryTextColor);
	border-top: 1px solid var(--builderSeparatorColor);
}

.warning {
	display: flex;
	align-items: center;
	background: var(--builderWarningColor);
	color: var(--builderWarningTextColor);
	border-radius: 4px;
	gap: 12px;
	margin: 12px 12px 0;
	padding: 12px;
}
</style>
