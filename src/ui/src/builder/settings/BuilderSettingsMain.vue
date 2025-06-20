<template>
	<div class="BuilderSettingsMain">
		<p
			v-if="componentDefinition.description"
			class="BuilderSettingsMain__description"
		>
			{{ componentDefinition.description }}
		</p>
		<p v-if="isReadOnly" class="BuilderSettingsMain__warning cmc-warning">
			<i class="material-symbols-outlined">warning</i>
			<span>
				This component is instantiated in code. All settings in this
				panel are read-only and cannot be edited.
			</span>
		</p>

		<div class="BuilderSettingsMain__section" :inert="isReadOnly">
			<BuilderSettingsProperties />
			<template v-if="displaySettings">
				<BuilderSettingsBinding v-if="isBindable" />
				<BuilderSettingsHandlers />
				<BuilderSettingsVisibility />
			</template>
		</div>

		<div class="BuilderSettingsMain__spacer"></div>

		<div class="BuilderSettingsMain__componentId">
			<p
				class="BuilderSettingsMain__componentId__text"
				@click="copyComponentId"
			>
				{{ ssbm.firstSelectedId.value }}
			</p>
			<WdsButton
				class="BuilderSettingsMain__componentId__btn"
				size="smallIcon"
				variant="tertiary"
				:data-writer-tooltip="
					isComponentIdCopied ? 'Copied!' : 'Copy block id'
				"
				data-automation-action="copy-component-id"
				@click="copyComponentId"
			>
				<span class="material-symbols-outlined"
					>{{ isComponentIdCopied ? "check" : "content_copy" }}
				</span>
			</WdsButton>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, watch, defineAsyncComponent } from "vue";
import injectionKeys from "@/injectionKeys";

import BuilderSettingsProperties from "./BuilderSettingsProperties.vue";
import BuilderSettingsBinding from "./BuilderSettingsBinding.vue";
import BuilderSettingsVisibility from "./BuilderSettingsVisibility.vue";
import BuilderAsyncLoader from "../BuilderAsyncLoader.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { useButtonClipboard } from "../useButtonClipboard";

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

const { copyText: copyComponentId, isCopied: isComponentIdCopied } =
	useButtonClipboard(computed(() => ssbm.firstSelectedId.value));

const isBindable = computed(() =>
	Object.values(componentDefinition.value?.events ?? {}).some(
		(e) => e.bindable,
	),
);
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderSettingsMain {
	display: flex;
	flex-direction: column;
}

.BuilderSettingsMain__description {
	padding: 24px;
	font-size: 14px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.BuilderSettingsMain__section {
	display: flex;
	flex-direction: column;
}

.BuilderSettingsMain__section > * {
	padding: 24px;
}

.BuilderSettingsMain__section > *:not(:first-child) {
	border-top: 1px solid var(--builderSeparatorColor);
}

.BuilderSettingsMain__section[inert] {
	opacity: 0.7;
}

.BuilderSettingsMain__spacer {
	flex-grow: 1;
}

.BuilderSettingsMain__componentId {
	color: var(--builderSecondaryTextColor);
	border-top: 1px solid var(--builderSeparatorColor);
	padding: 24px;
	display: grid;
	grid-template-columns: 1fr auto;
	align-items: center;
}
.BuilderSettingsMain__componentId__text {
	cursor: pointer;
}
.BuilderSettingsMain__componentId__btn {
	border: none;
}

.BuilderSettingsMain__warning {
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
