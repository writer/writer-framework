<script setup lang="ts">
import { useWorkflowRun } from "@/composables/useWorkflowRun";
import WdsButton from "@/wds/WdsButton.vue";
import injectionKeys from "@/injectionKeys";
import {
	computed,
	inject,
	ref,
	toRaw,
	useTemplateRef,
	watch,
	watchEffect,
} from "vue";
import { useFloating, offset } from "@floating-ui/vue";
import WorkflowToolbarBlocksDropdown from "./WorkflowToolbarBlocksDropdown.vue";
import { useFocusWithin } from "@/composables/useFocusWithin";

defineEmits({
	autogenClick: () => true,
});

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const workflowComponentId = inject(injectionKeys.componentId);

const startBlocks = computed(() => {
	const blocks = wf.getComponents(workflowComponentId);

	const blockIdsWithDeps = new Set();
	for (const block of blocks) {
		if (!block.outs?.length) continue;
		for (const out of block.outs) blockIdsWithDeps.add(out.toNodeId);
	}

	return blocks.filter((b) => !blockIdsWithDeps.has(b.id));
});

const isDropdownOpen = ref(false);

const seeWorkflowsBtn = useTemplateRef("seeWorkflowsBtn");
const dropdown = useTemplateRef("dropdown");

const { run: handleRun, isRunning } = useWorkflowRun(wf, workflowComponentId);

const { floatingStyles } = useFloating(seeWorkflowsBtn, dropdown, {
	placement: "bottom-end",
	middleware: [offset(12)],
});

const root = useTemplateRef("root");
const hasFocus = useFocusWithin(root);
watch(hasFocus, () => {
	if (!hasFocus.value && isDropdownOpen.value) isDropdownOpen.value = false;
});

function toggleDropdown() {
	isDropdownOpen.value = !isDropdownOpen.value;
	if (isDropdownOpen.value) {
		wfbm.isSettingsBarCollapsed.value = true;
	}
}

function jumpToComponent(componentId: string) {
	wfbm.setSelection(componentId, undefined, "click");
	isDropdownOpen.value = false;
}

function runBranch(componentId: string) {
	handleRun(componentId);
	isDropdownOpen.value = false;
}
</script>

<template>
	<div ref="root" class="WorkflowToolbar">
		<WdsButton
			variant="secondary"
			size="small"
			:data-writer-unselectable="true"
			data-automation-action="run-autogen"
			@click="$emit('autogenClick')"
		>
			<i class="material-symbols-outlined">bolt</i>
			Autogen
		</WdsButton>
		<div ref="seeWorkflowsBtn" class="WorkflowToolbar__btn">
			<WdsButton
				variant="secondary"
				size="small"
				:data-writer-unselectable="true"
				data-automation-action="run-workflow"
				@click="handleRun()"
			>
				<i class="material-symbols-outlined">play_arrow</i>
				{{ isRunning ? "Running..." : "Run blueprint" }}
			</WdsButton>
			<hr class="WorkflowToolbar__btn__divider" />
			<WdsButton
				v-if="startBlocks.length > 1"
				class="WorkflowToolbar__btn__dropdownTrigger"
				variant="secondary"
				size="smallIcon"
				custom-size="20px"
				@click="toggleDropdown"
			>
				<i class="material-symbols-outlined">{{
					isDropdownOpen ? "arrow_drop_up" : "arrow_drop_down"
				}}</i>
			</WdsButton>
		</div>
		<WorkflowToolbarBlocksDropdown
			v-if="isDropdownOpen"
			ref="dropdown"
			:style="floatingStyles"
			:blocks="startBlocks"
			@jump-to-component="jumpToComponent"
			@run-branch="runBranch"
		/>
	</div>
</template>

<style lang="css" scoped>
.WorkflowToolbar__btn {
	display: flex;
	background: var(--wdsColorBlack);
	border-radius: 300px;
	box-shadow: var(--buttonShadow);
	outline: none;
	border-style: solid;
	border-width: 1px;
	align-items: center;
	height: 42px;
	/* padding: 10px 20px 10px 20px; */
	gap: 8px;
	padding-left: 8px;
	padding-right: 8px;
}
.WorkflowToolbar__btn__dropdownTrigger {
	font-size: 20px;
}
.WorkflowToolbar__btn__divider {
	display: block;
	width: 1px;
	height: 100%;
	border: none;
	height: 24px;
	background: var(--wdsColorGray5);
}
</style>
