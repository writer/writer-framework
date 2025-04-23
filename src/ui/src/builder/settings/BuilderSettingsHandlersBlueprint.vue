<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { computed, inject, PropType } from "vue";
import { useComponentActions } from "../useComponentActions";
import { Component } from "@/writerTypes";
import WdsButton from "@/wds/WdsButton.vue";
import { useToasts } from "../useToast";
import BuilderListItem from "../BuilderListItem.vue";
import { useBlueprintsRun } from "@/composables/useBlueprintRun";
import { WdsColor } from "@/wds/tokens";
import BuilderBlueprintState from "../BuilderBlueprintState.vue";
import { useComponentLinkedBlueprints } from "@/composables/useComponentBlueprints";
import WdsButtonLink from "@/wds/WdsButtonLink.vue";
import { useSegmentTracking } from "@/composables/useSegmentTracking";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const props = defineProps({
	component: { type: Object as PropType<Component>, required: true },
	eventType: { type: String, required: true },
	eventDescription: { type: String, required: false, default: undefined },
});

const tracking = useSegmentTracking(wf);

const { createAndInsertComponent, removeComponentsSubtree } =
	useComponentActions(wf, wfbm, tracking);

const eventTypeFormated = computed(() =>
	props.eventType.replace(/^wf-/, "").replaceAll("-", " "),
);

const { blueprints: linkedBlueprints, triggers: linkedTriggers } =
	useComponentLinkedBlueprints(
		wf,
		computed(() => props.component.id),
		computed(() => props.eventType),
	);

const { run, isRunning } = useBlueprintsRun(
	wf,
	computed(() =>
		linkedTriggers.value.map((w) => ({
			blueprintId: w.parentId,
			branchId: w.id,
		})),
	),
);

const { pushToast } = useToasts();

function getNewBlueprintKey() {
	const indexes = linkedBlueprints.value.map((w) => {
		const matchs = (w.content.key ?? "0").match(/\d+/);
		return matchs ? Number(matchs[0]) : 0;
	});
	return indexes.length === 0 ? 1 : Math.max(...indexes) + 1;
}

async function createLinkedBlueprint() {
	const { type } = props.component;
	const { name, events } = wf.getComponentDefinition(type);
	const alias = `${name} - ${props.eventType}`;
	const key = `${type}@${props.eventType.replace(/^wf-/, "")}_${getNewBlueprintKey()}`;

	let defaultResult = events?.[props.eventType]?.eventPayloadExample;

	if (typeof defaultResult === "object" && defaultResult !== null) {
		defaultResult = JSON.stringify(defaultResult);
	}

	const blueprintId = createAndInsertComponent(
		"blueprints_blueprint",
		"blueprints_root",
		undefined,
		{
			content: {
				key,
			},
		},
		(parentId) => {
			createAndInsertComponent(
				"blueprints_uieventtrigger",
				parentId,
				undefined,
				{
					content: {
						alias,
						refComponentId: props.component.id,
						refEventType: props.eventType,
						defaultResult: defaultResult
							? String(defaultResult)
							: undefined,
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
			label: "Go to blueprint",
			func: () =>
				jumpToBlueprint(
					blueprintId,
					getBlueprintTriggerBlock(blueprintId)?.id,
				),
			icon: "linked_services",
		},
	});
}
function getBlueprintTriggerBlock(blueprintId: string) {
	return wf
		.getComponents(blueprintId)
		.find(
			(c) =>
				c.type === "blueprints_uieventtrigger" &&
				c.content.refComponentId === props.component.id &&
				c.content.refEventType === props.eventType,
		);
}

function deleteLinkedBlueprint(trigger: Component) {
	const componentsToDelete = [trigger.id];
	if (wf.getComponents(trigger.parentId).length === 1) {
		componentsToDelete.push(trigger.parentId);
	}
	removeComponentsSubtree(...componentsToDelete);
}

function getTriggerName(trigger: Component) {
	return wf.getComponentById(trigger.parentId)?.content?.key || "Blueprint";
}

function jumpToBlueprint(blueprintId: string, triggerId?: string) {
	wf.setActivePageId(blueprintId);
	wfbm.setMode("blueprints");
	wfbm.setSelection(triggerId ?? blueprintId, undefined, "click");
}
</script>

<template>
	<div class="BuilderSettingsHandlersBlueprint" :aria-busy="isRunning">
		<div class="BuilderSettingsHandlersBlueprint__title">
			<WdsButton
				class="BuilderSettingsHandlersBlueprint__title__btn"
				variant="special"
				size="icon"
				aria-label="Run the attached blueprints"
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

		<div class="BuilderSettingsHandlersBlueprint__list">
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
				<div class="BuilderSettingsHandlersBlueprint__list__item">
					<WdsButtonLink
						variant="secondary"
						:disabled="isRunning"
						:text="getTriggerName(trigger)"
						:data-writer-tooltip="getTriggerName(trigger)"
						data-writer-tooltip-strategy="overflow"
						@click="jumpToBlueprint(trigger.parentId, trigger.id)"
					/>
					<BuilderBlueprintState :blueprint-id="trigger.parentId" />
					<WdsButton
						variant="neutral"
						size="smallIcon"
						custom-size="18px"
						aria-label="Unlink blueprint"
						data-writer-tooltip="This will remove the trigger but will not delete the blueprint"
						:disabled="isRunning"
						@click="deleteLinkedBlueprint(trigger)"
					>
						<i class="material-symbols-outlined">link_off</i>
					</WdsButton>
				</div>
			</BuilderListItem>
			<BuilderListItem is-last :color="WdsColor.Blue2">
				<div class="BuilderSettingsHandlersBlueprint__list__item">
					<WdsButtonLink
						variant="primary"
						weight="semibold"
						:disabled="isRunning"
						left-icon="add"
						text="Create blueprint"
						@click="createLinkedBlueprint"
					/>
				</div>
			</BuilderListItem>
		</div>
	</div>
</template>

<style lang="css" scoped>
.BuilderSettingsHandlersBlueprint {
	font-size: 14px;
}
.BuilderSettingsHandlersBlueprint__title {
	display: flex;
	gap: 8px;
	align-items: center;
}
.BuilderSettingsHandlersBlueprint__title__btn {
	min-width: 40px;
}
.BuilderSettingsHandlersBlueprint__title__btn i {
	font-size: 24px;
}
.BuilderSettingsHandlersBlueprint__list {
	column-gap: 12px;
	padding-left: 19px;
}
.BuilderSettingsHandlersBlueprint__list__item {
	padding-top: 6px;
	padding-bottom: 6px;
	padding-left: 12px;

	display: grid;
	grid-template-columns: minmax(0, 1fr) auto auto;
	justify-content: space-between;
	gap: 4px;
}
</style>
