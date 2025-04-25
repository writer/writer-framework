<script setup lang="ts">
import { useBlueprintRun } from "@/composables/useBlueprintRun";
import WdsButton from "@/wds/WdsButton.vue";
import WdsButtonSplit from "@/wds/WdsButtonSplit.vue";
import injectionKeys from "@/injectionKeys";
import { computed, inject, shallowRef, toRaw, useTemplateRef } from "vue";
import BlueprintToolbarBlocksDropdown from "./BlueprintToolbarBlocksDropdown.vue";
import { useWriterTracking } from "@/composables/useWriterTracking";

defineEmits({
	autogenClick: () => true,
});

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const blueprintComponentId = inject(injectionKeys.componentId);

const runBlueprintBtn = useTemplateRef("runBlueprintBtn");

const tracking = useWriterTracking(wf);

const { run: handleRun, isRunning } = useBlueprintRun(wf, blueprintComponentId);

const triggerComponents = computed(() =>
	wf
		.getComponents(blueprintComponentId)
		.filter(
			(c) => wf.getComponentDefinition(c.type)?.category === "Triggers",
		),
);

const previousSelection = shallowRef<typeof wfbm.selection.value>([]);

function onDropdownOpen() {
	previousSelection.value = toRaw(wfbm.selection.value);
	wfbm.setSelection(null);
}

function onDropdownClose() {
	if (!previousSelection.value?.length) return;
	wfbm.setSelection(null);
	for (const s of previousSelection.value) {
		wfbm.appendSelection(s.componentId, s.instancePath, s.source);
	}
	previousSelection.value = [];
}

function jumpToComponent(componentId: string) {
	wfbm.setSelection(componentId, undefined, "click");
	runBlueprintBtn.value?.toggleDropdown(false);
}

async function runBlueprint(componentId?: string) {
	runBlueprintBtn.value?.toggleDropdown(false);
	await handleRun(componentId);
}
</script>

<template>
	<div ref="root" class="BlueprintToolbar" :data-writer-unselectable="true">
		<WdsButton
			variant="secondary"
			data-automation-action="run-autogen"
			@click="$emit('autogenClick')"
		>
			<i class="material-symbols-outlined">bolt</i>
			Autogen
		</WdsButton>
		<WdsButtonSplit
			v-if="triggerComponents.length"
			ref="runBlueprintBtn"
			class="BlueprintToolbar__runBlueprintDropdown"
			variant="secondary"
			:disabled="isRunning"
			@main-click="runBlueprint()"
			@dropdown-open="onDropdownOpen"
			@dropdown-close="onDropdownClose"
		>
			<template #button>
				<i class="material-symbols-outlined">play_arrow</i>
				{{ isRunning ? "Running..." : "Run blueprint" }}
			</template>
			<template #dropdown>
				<BlueprintToolbarBlocksDropdown
					:components="triggerComponents"
					@jump-to-component="jumpToComponent"
					@run-branch="runBlueprint($event)"
				/>
			</template>
		</WdsButtonSplit>
		<WdsButton
			v-else
			class="BlueprintToolbar__runBlueprint"
			data-automation-action="run-blueprint"
			variant="secondary"
			:disabled="isRunning"
			@click="runBlueprint()"
		>
			<i class="material-symbols-outlined">play_arrow</i>
			{{ isRunning ? "Running..." : "Run blueprint" }}
		</WdsButton>
	</div>
</template>

<style lang="css" scoped>
.BlueprintToolbar__runBlueprint {
	min-width: 160px;
}
.BlueprintToolbar__runBlueprintDropdown {
	min-width: 185px;
}
</style>
