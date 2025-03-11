<script setup lang="ts">
import { useWorkflowRun } from "@/composables/useWorkflowRun";
import WdsButton from "@/wds/WdsButton.vue";
import injectionKeys from "@/injectionKeys";
import {
	computed,
	inject,
	ref,
	shallowRef,
	toRaw,
	useTemplateRef,
	watch,
} from "vue";
import { useFloating, offset } from "@floating-ui/vue";
import WorkflowToolbarBlocksDropdown from "./WorkflowToolbarBlocksDropdown.vue";
import { useFocusWithin } from "@/composables/useFocusWithin";
import BaseTransitionSlideFade from "@/components/core/base/BaseTransitionSlideFade.vue";

defineEmits({
	autogenClick: () => true,
});

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const workflowComponentId = inject(injectionKeys.componentId);

const root = useTemplateRef("root");
const dropdown = useTemplateRef("dropdown");

const { run: handleRun, isRunning } = useWorkflowRun(wf, workflowComponentId);

const { floatingStyles } = useFloating(root, dropdown, {
	placement: "bottom-end",
	middleware: [offset(12)],
});

const hasFocus = useFocusWithin(root);
watch(hasFocus, () => {
	if (!hasFocus.value && isDropdownOpen.value) isDropdownOpen.value = false;
});

const triggerComponents = computed(() =>
	wf
		.getComponents(workflowComponentId)
		.filter(
			(c) => wf.getComponentDefinition(c.type)?.category === "Triggers",
		),
);

const isDropdownOpen = ref(false);

const previousSelection = shallowRef<typeof wfbm.selection.value>([]);

function toggleDropdown() {
	isDropdownOpen.value = !isDropdownOpen.value;
	if (isDropdownOpen.value) {
		previousSelection.value = toRaw(wfbm.selection.value);
		wfbm.setSelection(null);
	} else if (previousSelection.value?.length) {
		wfbm.setSelection(null);
		for (const s of previousSelection.value) {
			wfbm.appendSelection(s.componentId, s.instancePath, s.source);
		}
		previousSelection.value = [];
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
	<div ref="root" class="WorkflowToolbar" :data-writer-unselectable="true">
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
				data-automation-action="run-workflow"
				@click.stop="handleRun()"
			>
				<i class="material-symbols-outlined">play_arrow</i>
				{{ isRunning ? "Running..." : "Run blueprint" }}
			</WdsButton>
			<template v-if="triggerComponents.length > 1">
				<hr class="WorkflowToolbar__btn__divider" />
				<WdsButton
					class="WorkflowToolbar__btn__dropdownTrigger"
					variant="secondary"
					size="smallIcon"
					custom-size="20px"
					@click.capture="toggleDropdown"
				>
					<i class="material-symbols-outlined">{{
						isDropdownOpen ? "arrow_drop_up" : "arrow_drop_down"
					}}</i>
				</WdsButton>
			</template>
			<BaseTransitionSlideFade>
				<WorkflowToolbarBlocksDropdown
					v-if="isDropdownOpen"
					ref="dropdown"
					:style="floatingStyles"
					:components="triggerComponents"
					@jump-to-component="jumpToComponent"
					@run-branch="runBranch"
				/>
			</BaseTransitionSlideFade>
		</div>
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
