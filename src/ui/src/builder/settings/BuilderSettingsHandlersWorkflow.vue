<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { computed, inject, PropType } from "vue";
import { useComponentActions } from "../useComponentActions";
import { Component } from "@/writerTypes";
import WdsButton from "@/wds/WdsButton.vue";
import { useToasts } from "../useToast";
import { WdsColor } from "@/wds/tokens";

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

const linkedWorkflows = computed(() => {
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

const { pushToast } = useToasts();

async function createLinkedWorkflow() {
	const { type } = props.component;
	const { name } = wf.getComponentDefinition(type);
	const alias = `${name} - ${props.eventType}`;
	const key = `${type}@${props.eventType.replace(/^wf-/, "")}`;
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
			label: "Go to archestration",
			func: () => jumpToWorkflow(workflowId),
			icon: "linked_services",
		},
	});
}

function jumpToWorkflow(workflowId: string) {
	wf.setActivePageId(workflowId);
	wfbm.setMode("workflows");
	wfbm.setSelection(workflowId);
}
</script>

<template>
	<div class="BuilderSettingsHandlersWorkflow">
		<WdsButton variant="tertiary" @click="createLinkedWorkflow">
			<i class="material-symbols-outlined">add</i>Create linked workflow
		</WdsButton>

		<div class="BuilderSettingsHandlersWorkflow__title">
			<WdsButton
				variant="special"
				size="icon"
				@click="createLinkedWorkflow"
			>
				<i class="material-symbols-outlined">play_arrow</i>
			</WdsButton>
			<p>{{ eventTypeFormated }}</p>
		</div>

		<div class="BuilderSettingsHandlersWorkflow__list">
			<template
				v-for="(workflow, i) of linkedWorkflows"
				:key="workflow.id"
			>
				<div class="BuilderSettingsHandlersWorkflow__list__anchor">
					<svg
						width="17"
						viewBox="0 0 17 28"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
						preserveAspectRatio="xMinYMax meet"
					>
						<path
							d="M1 0V19C1 23.4183 4.58172 27 9 27H17"
							:stroke="WdsColor.Blue2"
						/>
						<path
							v-if="linkedWorkflows.length !== i + 1"
							d="M1 0 V28"
							:stroke="WdsColor.Blue2"
						/>
					</svg>
				</div>
				<div class="BuilderSettingsHandlersWorkflow__list__item">
					<button
						role="button"
						class="BuilderSettingsHandlersWorkflow__list__item__btn"
						@click="jumpToWorkflow(workflow.id)"
					>
						{{ workflow.content.key || "Workflow" }}
					</button>
				</div>
			</template>
		</div>
	</div>
</template>

<style lang="css" scoped>
.BuilderSettingsHandlersWorkflow__title {
	display: flex;
	gap: 8px;
	align-items: center;
	font-size: 14px;
}

.BuilderSettingsHandlersWorkflow__list {
	display: grid;
	grid-template-columns: auto 1fr;
	column-gap: 12px;
	padding-left: 20px;
}
.BuilderSettingsHandlersWorkflow__list__item {
	padding-top: 6px;
	padding-bottom: 6px;
}

.BuilderSettingsHandlersWorkflow__list__anchor {
	/* background-color: coral; */
	width: 20px;
	height: 100%;
}
.BuilderSettingsHandlersWorkflow__list__anchor_img {
	height: 100%;
}

.BuilderSettingsHandlersWorkflow__list__item__btn {
	background-color: transparent;
	border: none;
	text-align: left;
	padding: 0;
	cursor: pointer;
}
.BuilderSettingsHandlersWorkflow__list__item__btn:hover {
	text-decoration: underline;
}
</style>
