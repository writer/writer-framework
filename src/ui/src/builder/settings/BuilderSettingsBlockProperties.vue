<template>
	<BuilderSettingsProperties :group-level="0"></BuilderSettingsProperties>
	<template v-if="displaySettings">
		<BuilderSettingsBinding v-if="isBindable"></BuilderSettingsBinding>
		<BuilderSettingsHandlers></BuilderSettingsHandlers>
		<BuilderSettingsVisibility></BuilderSettingsVisibility>
	</template>
	<BuilderSettingsAPICode>Execute via API</BuilderSettingsAPICode>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, inject } from "vue";
import injectionKeys from "@/injectionKeys";

import BuilderSettingsAPICode from "@/builder/settings/BuilderSettingsAPICode.vue";
import BuilderSettingsBinding from "@/builder/settings/BuilderSettingsBinding.vue";
import BuilderSettingsVisibility from "@/builder/settings/BuilderSettingsVisibility.vue";
import BuilderSettingsProperties from "@/builder/settings/BuilderSettingsProperties.vue";
import BuilderAsyncLoader from "@/builder/BuilderAsyncLoader.vue";

const BuilderSettingsHandlers = defineAsyncComponent({
	loader: () => import("./BuilderSettingsHandlers.vue"),
	loadingComponent: BuilderAsyncLoader,
});

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);

const componentDefinition = computed(() => {
	const { type } = component.value;
	const definition = wf.getComponentDefinition(type);
	return definition;
});

const displaySettings = computed(() => {
	if (!ssbm.isSingleSelectionActive.value) return false;

	return (
		!componentDefinition.value.toolkit ||
		componentDefinition.value.toolkit == "core"
	);
});

const isBindable = computed(() =>
	Object.values(componentDefinition.value?.events ?? {}).some(
		(e) => e.bindable,
	),
);
</script>
