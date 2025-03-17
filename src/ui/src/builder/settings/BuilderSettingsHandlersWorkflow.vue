<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { computed, inject, PropType } from "vue";
import { useComponentActions } from "../useComponentActions";
import { Component } from "@/writerTypes";
import WdsButton from "@/wds/WdsButton.vue";
import { useToasts } from "../useToast";
import BuilderListItem from "../BuilderListItem.vue";
import {
	useWorkflowsRun,
	WorkflowsRunListItem,
} from "@/composables/useWorkflowRun";
import { WdsColor } from "@/wds/tokens";
import BuilderWorkflowState from "../BuilderWorkflowState.vue";
import { useComponentLinkedWorkflows } from "@/composables/useComponentWorkflows";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const props = defineProps({
	component: { type: Object as PropType<Component>, required: true },
	eventType: { type: String, required: true },
	eventDescription: { type: String, required: false, default: undefined },
});

const { createAndInsertComponent, removeComponentSubtree } =
	useComponentActions(wf, wfbm);

const eventTypeFormated = computed(() =>
	props.eventType.replace(/^wf-/, "").replaceAll("-", " "),
);

const { workflows: linkedWorkflows, triggers: linkedTriggers } =
	useComponentLinkedWorkflows(
		wf,
		computed(() => props.component.id),
		computed(() => props.eventType),
	);

const { run, isRunning } = useWorkflowsRun(
	wf,
	computed(() =>
		linkedTriggers.value.map((w) => ({
			workflowId: w.parentId,
			branchId: w.id,
		})),
	),
);

const { pushToast } = useToasts();

function getNewWorkflowKey() {
	const indexes = linkedWorkflows.value.map((w) => {
		const matchs = (w.content.key ?? "0").match(/\d+/);
		return matchs ? Number(matchs[0]) : 0;
	});
	return indexes.length === 0 ? 1 : Math.max(...indexes) + 1;
}

async function createLinkedWorkflow() {
	const { type } = props.component;
	const { name } = wf.getComponentDefinition(type);
	const alias = `${name} - ${props.eventType}`;
	const key = `${type}@${props.eventType.replace(/^wf-/, "")}_${getNewWorkflowKey()}`;
	const workflowId = createAndInsertComponent(
		"workflows_workflow",
		"workflows_root",
		undefined,
		{
			content: {
				key,
			},
		},
		(parentId) => {
			createAndInsertComponent(
				"workflows_uieventtrigger",
				parentId,
				undefined,
				{
					content: {
						alias,
						refComponentId: props.component.id,
						refEventType: props.eventType,
					},
					x: 96,
					y: 96,
				},
			);
		},
	);
	pushToast({
		type: "success",
		message: `${alias} added`,
		action: {
			label: "Go to workflow",
			func: () =>
				jumpToWorkflow(
					workflowId,
					getWorkflowTriggerBlock(workflowId)?.id,
				),
			icon: "linked_services",
		},
	});
}
function getWorkflowTriggerBlock(workflowId: string) {
	return wf
		.getComponents(workflowId)
		.find(
			(c) =>
				c.type === "workflows_uieventtrigger" &&
				c.content.refComponentId === props.component.id &&
				c.content.refEventType === props.eventType,
		);
}

function deleteLinkedWorkflow(workflowId: string) {
	const block = getWorkflowTriggerBlock(workflowId);
	if (block === undefined) return;

	removeComponentSubtree(block.id);
}

function getTriggerName(trigger: Component) {
	return wf.getComponentById(trigger.parentId)?.content?.key || "Workflow";
}

function jumpToWorkflow(workflowId: string, triggerId?: string) {
	wf.setActivePageId(workflowId);
	wfbm.setMode("workflows");
	wfbm.setSelection(triggerId ?? workflowId, undefined, "click");
}
</script>

<template>
	<div class="BuilderSettingsHandlersWorkflow" :aria-busy="isRunning">
		<div class="BuilderSettingsHandlersWorkflow__title">
			<WdsButton
				class="BuilderSettingsHandlersWorkflow__title__btn"
				variant="special"
				size="icon"
				aria-label="Run the attached workflows"
				:disabled="isRunning"
				:loading="isRunning"
				@click="run"
			>
				<i class="material-symbols-outlined">play_arrow</i>
			</WdsButton>
			<p>{{ eventTypeFormated }}</p>
			<span
				v-if="eventDescription"
				:data-writer-tooltip="eventDescription"
				class="material-symbols-outlined"
				>help</span
			>
		</div>

		<div class="BuilderSettingsHandlersWorkflow__list">
			<BuilderListItem
				v-for="(trigger, i) of linkedTriggers"
				:key="trigger.id"
				:color="WdsColor.Blue6"
				:color-last="
					linkedTriggers.length === i + 1
						? WdsColor.Blue2
						: WdsColor.Blue6
				"
			>
				<div class="BuilderSettingsHandlersWorkflow__list__item">
					<button
						role="button"
						class="BuilderSettingsHandlersWorkflow__list__item__btn"
						@click="jumpToWorkflow(trigger.parentId, trigger.id)"
					>
						{{ getTriggerName(trigger) }}
					</button>
					<BuilderWorkflowState :workflow-id="trigger.parentId" />
					<WdsButton
						variant="neutral"
						size="smallIcon"
						custom-size="18px"
						aria-label="Unlink Orchestration"
						data-writer-tooltip="This will remove the trigger but will not delete the workflow"
						:disabled="isRunning"
						@click="deleteLinkedWorkflow(trigger.id)"
					>
						<i class="material-symbols-outlined">link_off</i>
					</WdsButton>
				</div>
			</BuilderListItem>
			<BuilderListItem is-last :color="WdsColor.Blue2">
				<div class="BuilderSettingsHandlersWorkflow__list__item">
					<button
						role="button"
						class="BuilderSettingsHandlersWorkflow__list__item__btn BuilderSettingsHandlersWorkflow__list__item__btn--primary"
						:disabled="isRunning"
						@click="createLinkedWorkflow"
					>
						<i class="material-symbols-outlined">add</i>
						Connect new workflow
					</button>
				</div>
			</BuilderListItem>
		</div>
	</div>
</template>

<style lang="css" scoped>
.BuilderSettingsHandlersWorkflow {
	font-size: 14px;
}
.BuilderSettingsHandlersWorkflow__title {
	display: flex;
	gap: 8px;
	align-items: center;
}
.BuilderSettingsHandlersWorkflow__title__btn {
	min-width: 40px;
}
.BuilderSettingsHandlersWorkflow__title__btn i {
	font-size: 24px;
}
.BuilderSettingsHandlersWorkflow__list {
	column-gap: 12px;
	padding-left: 19px;
}
.BuilderSettingsHandlersWorkflow__list__item {
	padding-top: 6px;
	padding-bottom: 6px;
	padding-left: 12px;

	display: flex;
	justify-content: space-between;
	gap: 4px;
}

.BuilderSettingsHandlersWorkflow__list__item__btn {
	background-color: transparent;
	border: none;
	padding: 0;
	cursor: pointer;

	display: flex;
	align-items: center;
	justify-content: flex-start;
	gap: 8px;

	flex-grow: 1;
}
.BuilderSettingsHandlersWorkflow__list__item__btn:hover {
	text-decoration: underline;
}
.BuilderSettingsHandlersWorkflow__list__item__btn--primary {
	color: var(--wdsColorBlue5);
	font-weight: 500;
}
.BuilderSettingsHandlersWorkflow__list__item__btn--primary:hover {
	text-decoration: unset;
}
</style>
