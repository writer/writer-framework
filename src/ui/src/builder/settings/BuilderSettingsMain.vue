<template>
	<div class="BuilderSettingsMain">
		<p
			v-if="componentDefinition.description"
			class="BuilderSettingsMain__description"
		>
			{{ componentDefinition.description }}
		</p>
		<p v-if="isReadOnly" class="warning cmc-warning">
			<i class="material-symbols-outlined">warning</i>
			<span>
				This component is instantiated in code. All settings in this
				panel are read-only and cannot be edited.
			</span>
		</p>

		<div class="sections" :inert="isReadOnly">
			<BuilderSettingsProperties />
			<template v-if="displaySettings">
				<BuilderSettingsBinding v-if="isBindable" />
				<BuilderSettingsHandlers />
				<BuilderSettingsVisibility />
			</template>
		</div>

		<div class="sections debug">
			<p>
				Component id:
				<BuilderCopyText>{{
					ssbm.firstSelectedId.value
				}}</BuilderCopyText>
			</p>
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

const BuilderSettingsHandlers = defineAsyncComponent({
	loader: () => import("./BuilderSettingsHandlers.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);
const isReadOnly = computed(() => component.value.isCodeManaged);

const displaySettings = computed(() => {
	if (!ssbm.isSingleSelectionActive.value) return false;

	return (
		!componentDefinition.value.toolkit ||
		componentDefinition.value.toolkit == "core"
	);
});

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

.BuilderSettingsMain__description {
	padding: 24px;
	font-size: 14px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

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
