<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { computed, inject, PropType } from "vue";
import { useComponentActions } from "../useComponentActions";
import { Component } from "@/writerTypes";
import WdsButton from "@/wds/WdsButton.vue";
import { useToasts } from "../useToast";
import BuilderListItem from "../BuilderListItem.vue";
import { useWorkflowsRun } from "@/composables/useWorkflowRun";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const props = defineProps({
	component: { type: Object as PropType<Component>, required: true },
	eventType: { type: String, required: true },
});

const { createAndInsertComponent } = useComponentActions(wf, wfbm);

const eventTypeFormated = computed(() =>
	props.eventType.replace(/^wf-/, "").replaceAll("-", " "),
);

const linkedWorkflows = computed<Component[]>(() => {
	return wf
		.getComponents("workflows_root")
		.filter((w) =>
			wf
				.getComponents(w.id)
				.some(
					(c) =>
						c.type === "workflows_uieventtrigger" &&
						c.content.refComponentId === props.component.id &&
						c.content.refEventType === props.eventType,
				),
		);
});
const linkedWorkflowsIds = computed(() =>
	linkedWorkflows.value.map((w) => w.id),
);

const { run, isRunning } = useWorkflowsRun(wf, linkedWorkflowsIds);

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
			func: () => jumpToWorkflow(workflowId),
			icon: "linked_services",
		},
	});
}

function deleteLinkedWorkflow(workflowId: string) {
	const block = wf
		.getComponents(workflowId)
		.find(
			(c) =>
				c.type === "workflows_uieventtrigger" &&
				c.content.refComponentId === props.component.id &&
				c.content.refEventType === props.eventType,
		);
	if (block === undefined) return;

	wf.deleteComponent(block.id);
}

function jumpToWorkflow(workflowId: string) {
	wf.setActivePageId(workflowId);
	wfbm.setMode("workflows");
	wfbm.setSelection(workflowId);
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
		</div>

		<div class="BuilderSettingsHandlersWorkflow__list">
			<BuilderListItem
				v-for="workflow of linkedWorkflows"
				:key="workflow.id"
			>
				<div class="BuilderSettingsHandlersWorkflow__list__item">
					<button
						role="button"
						class="BuilderSettingsHandlersWorkflow__list__item__btn"
						@click="jumpToWorkflow(workflow.id)"
					>
						{{ workflow.content.key || "Workflow" }}
					</button>
					<WdsButton
						variant="neutral"
						size="smallIcon"
						aria-label="Unlink Orchestration"
						data-writer-tooltip="This will remove the trigger but will not delete the Orchestration"
						:disabled="isRunning"
						@click="deleteLinkedWorkflow(workflow.id)"
					>
						<i class="material-symbols-outlined">link_off</i>
					</WdsButton>
				</div>
			</BuilderListItem>
			<BuilderListItem is-last>
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
}

.BuilderSettingsHandlersWorkflow__list__item__btn {
	background-color: transparent;
	border: none;
	text-align: left;
	padding: 0;
	cursor: pointer;

	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
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
