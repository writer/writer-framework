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
			<BuilderSettingsGroupBlockProperties v-if="isGroupNode" />
			<BuilderSettingsBlockProperties v-else />
		</div>

		<div class="sections debug">
			<div>
				Component id:
				<BuilderCopyText>{{
					ssbm.firstSelectedId.value
				}}</BuilderCopyText>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, watch } from "vue";
import injectionKeys from "@/injectionKeys";

import BuilderCopyText from "../BuilderCopyText.vue";
import BuilderSettingsBlockProperties from "@/builder/settings/BuilderSettingsBlockProperties.vue";
import BuilderSettingsGroupBlockProperties from "@/builder/settings/BuilderSettingsGroupBlockProperties.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(ssbm.firstSelectedId.value),
);

const isReadOnly = computed(() => component.value.isCodeManaged);

const isGroupNode = computed(() => {
	return wf.isGroupNode(component.value.type);
});

watch(component, (newComponent) => {
	if (!newComponent) ssbm.setSelection(null);
});
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
