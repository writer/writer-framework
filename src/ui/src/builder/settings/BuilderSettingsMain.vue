<template>
	<div class="BuilderSettingsMain">
		<p
			v-if="componentDefinition.description"
			class="BuilderSettingsMain__description"
		>
			{{ componentDefinition.description }}
		</p>
		<p v-if="isReadOnly" class="BuilderSettingsMain__warning cmc-warning">
			<span>
				<WdsIcon name="triangle-alert" />
			</span>
			<span>
				This component is instantiated in code. All settings in this
				panel are read-only and cannot be edited.
			</span>
		</p>

		<div class="BuilderSettingsMain__section">
			<BuilderSettingsProperties :is-read-only="isReadOnly" />
			<component
				:is="artifactRegistry[a.key]"
				v-for="a in artifactsTop"
				:key="a.key"
				:inert="isReadOnly"
			/>
			<template v-if="displaySettings">
				<BuilderSettingsBinding
					v-if="isBindable"
					:is-read-only="isReadOnly"
				/>
				<BuilderSettingsHandlers :is-read-only="isReadOnly" />
				<BuilderSettingsVisibility :is-read-only="isReadOnly" />
			</template>
			<component
				:is="artifactRegistry[a.key]"
				v-for="a in artifactsBottom"
				:key="a.key"
				:inert="isReadOnly"
			/>
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
				<WdsIcon :name="isComponentIdCopied ? 'check' : 'clipboard'" />
			</WdsButton>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, watch } from "vue";
import injectionKeys from "@/injectionKeys";
import BuilderSettingsProperties from "./BuilderSettingsProperties.vue";
import BuilderSettingsBinding from "./BuilderSettingsBinding.vue";
import BuilderSettingsVisibility from "./BuilderSettingsVisibility.vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { useButtonClipboard } from "../useButtonClipboard";
import { artifactRegistry } from "./artifacts";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const BuilderSettingsHandlers = defineAsyncComponentWithLoader({
	loader: () => import("./BuilderSettingsHandlers.vue"),
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

const artifactsTop = computed(() =>
	(componentDefinition.value?.settingsArtifacts ?? []).filter(
		(a) => a.position !== "bottom",
	),
);
const artifactsBottom = computed(() =>
	(componentDefinition.value?.settingsArtifacts ?? []).filter(
		(a) => a.position === "bottom",
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

.BuilderSettingsMain__section > *[inert] {
	opacity: 0.7;
}

.BuilderSettingsMain__section > *:not(:first-child) {
	border-top: 1px solid var(--builderSeparatorColor);
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
