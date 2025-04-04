<template>
	<div class="BuilderLogBlueprintExecution">
		<BuilderListItem
			v-for="(item, itemId) in enrichedExecutionLog.summary"
			:key="itemId"
			:is-last="itemId + 1 === enrichedExecutionLog.summary.length"
		>
			<div
				class="itemWrapper"
				:class="{
					'itemWrapper--first': itemId === 0,
					'itemWrapper--last':
						itemId + 1 === enrichedExecutionLog.summary.length,
				}"
			>
				<div
					class="item"
					:class="{
						selected: wfbm.isComponentIdSelected(item.componentId),
					}"
				>
					<div class="name">
						<div v-if="item.component?.['content']?.['alias']">
							<div class="eyebrow">
								{{
									item.componentDef?.name ??
									"Unavailable component"
								}}
							</div>
							{{ item.component?.["content"]?.["alias"] }}
						</div>
						<template v-else>
							{{
								item.componentDef?.name ??
								"Unavailable component"
							}}
						</template>
						<WdsButton
							v-if="item.component"
							variant="neutral"
							size="smallIcon"
							data-writer-tooltip="Jump to this block"
							@click="selectBlock(item.componentId)"
						>
							<i class="material-symbols-outlined"
								>jump_to_element</i
							>
						</WdsButton>
					</div>
					<div class="outcome">
						<template v-if="item.outcome !== 'in_progress'">
							<div
								class="ball"
								:class="
									item.componentDef?.outs?.[item.outcome]
										?.style
								"
							></div>

							{{
								item.componentDef?.outs?.[item.outcome]?.name ??
								item.outcome
							}}
						</template>
						<template v-else>
							<div class="ballContainer">
								<div class="ball inProgress"></div>
							</div>

							In progress...
						</template>
					</div>
					<div class="result">
						<WdsModal
							v-if="displayedItemId == itemId"
							title="Trace"
							size="wide"
							:actions="[
								{
									desc: 'Done',
									fn: () => (displayedItemId = null),
								},
							]"
						>
							<BuilderLogBlueprintExecutionTrace
								:execution-item="item"
								@close-modal="() => (displayedItemId = null)"
							></BuilderLogBlueprintExecutionTrace>
						</WdsModal>
						<WdsButton
							v-if="
								item.result ||
								item.returnValue ||
								item.executionEnvironment
							"
							variant="special"
							size="small"
							@click="() => (displayedItemId = itemId)"
						>
							<i class="material-symbols-outlined"
								>find_in_page</i
							>
							Trace
						</WdsButton>
					</div>
					<div class="time">
						{{ formatExecutionTime(item.executionTimeInSeconds) }}
					</div>
					<div
						v-if="item.message"
						v-dompurify-html="marked.parse(item.message)"
						class="message markdown"
					></div>
				</div>
			</div>
		</BuilderListItem>
	</div>
</template>

<script setup lang="ts">
import { marked } from "marked";
import injectionKeys from "@/injectionKeys";
import { BlueprintExecutionLog } from "../builderManager";
import { computed, inject, nextTick, ref } from "vue";
import { Component, WriterComponentDefinition } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderLogBlueprintExecutionTrace from "./BuilderLogBlueprintExecutionTrace.vue";
import WdsModal from "@/wds/WdsModal.vue";
import BuilderListItem from "../BuilderListItem.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

const props = defineProps<{
	executionLog: BlueprintExecutionLog;
}>();
const displayedItemId = ref<number | null>(null);

type EnrichedExecutionLog = BlueprintExecutionLog & {
	summary: {
		component?: Component;
		componentDef?: WriterComponentDefinition;
	}[];
};

const enrichedExecutionLog = computed(() => {
	const eLog: EnrichedExecutionLog = {
		summary: [
			...props.executionLog.summary
				.filter((item) => Boolean(item.outcome))
				.map((item) => ({
					...item,
					component: wf.getComponentById(item.componentId),
					componentDef: wf.getComponentById(item.componentId)
						? wf.getComponentDefinition(
								wf.getComponentById(item.componentId).type,
							)
						: undefined,
				})),
		],
	};
	return eLog;
});

async function selectBlock(componentId: Component["id"]) {
	wfbm.setMode("blueprints");
	await nextTick();
	goToComponentParentPage(componentId);
	await nextTick();
	wfbm.setSelection(componentId, undefined, "log");
}

function formatExecutionTime(timeInSeconds: number): string {
	if (timeInSeconds < 0) {
		return "N/A";
	}
	if (timeInSeconds < 0.1) {
		return "< 0.1s";
	}
	return `${timeInSeconds.toFixed(2)}s`;
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderLogBlueprintExecution {
	display: flex;
	flex-direction: column;
	margin-left: 19px;
}

.itemWrapper {
	margin-top: 6px;
	margin-bottom: 6px;
}
.itemWrapper--first {
	margin-top: 12px;
}
.itemWrapper--last {
	margin-bottom: unset;
}

.item {
	display: grid;
	grid-template-columns: 1fr 0.5fr 120px 80px;
	grid-template-rows: 1fr auto;
	column-gap: 16px;
	align-items: center;
	padding: 8px;
	border-radius: 6px;
	border: 1px solid var(--builderSeparatorColor);
}

.item.selected {
	border-left: 8px solid var(--builderSelectedColor);
}

.item .name {
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	display: flex;
	gap: 8px;
	align-items: center;
}

.item .name .eyebrow {
	color: var(--secondaryTextColor);
	font-size: 12px;
}

.item .outcome {
	grid-column: 2 / 3;
	grid-row: 1 / 2;
	display: flex;
	gap: 8px;
	align-items: center;
}

.item .outcome .ball {
	height: 8px;
	width: 8px;
	border-radius: 50%;
}

.item .outcome .ball.success {
	background: var(--wdsColorGreen5);
}

.item .outcome .ball.error {
	background: var(--wdsColorOrange5);
}

.item .outcome .ball.dynamic {
	background: var(--wdsColorPurple4);
}

.item .outcome .ballContainer {
	margin-left: -2px;
	margin-top: -2px;
	width: 12px;
	height: 12px;
	border-radius: 50%;
	padding: 2px;
	background: conic-gradient(#6985ff, #e4e9ff);
	animation: spin 0.8s linear infinite;
}

.item .outcome .ball.inProgress {
	background: #6985ff;
}

@keyframes spin {
	0% {
		transform: rotate(0deg);
		transform-origin: center;
	}
	100% {
		transform: rotate(360deg);
	}
}

.item .result {
	grid-column: 3 / 4;
	grid-row: 1 / 2;
}

.item .time {
	grid-column: 4 / 5;
	grid-row: 1 / 2;
}

.item .message {
	grid-column: 1 / 5;
	grid-row: 2 / 3;
	margin-top: 8px;
	border-top: 1px solid var(--builderSeparatorColor);
	padding-top: 16px;
	padding-bottom: 8px;
}

.markdown :deep(code) {
	font-family: monospace;
	font-size: 13px;
	background-color: rgba(0, 0, 0, 0.05);
	padding: 2px;
}
</style>
