<template>
	<div class="BuilderLogWorkflowExecution">
		<div
			v-for="(item, itemId) in enrichedExecutionLog.summary"
			:key="itemId"
			class="row"
		>
			<div class="marker top"></div>
			<div class="marker bottom"></div>
			<div class="item">
				<div class="name">
					{{ item.componentDef.name }}
					<WdsButton
						variant="neutral"
						size="smallIcon"
						data-writer-tooltip="Jump to this block"
						@click="selectBlock(item.componentId)"
					>
						<i class="material-symbols-outlined">jump_to_element</i>
					</WdsButton>
				</div>
				<div class="outcome">
					<div
						class="ball"
						:class="item.componentDef.outs[item.outcome]?.style"
					></div>
					{{
						item.componentDef.outs[item.outcome]?.name ??
						item.outcome
					}}
				</div>
				<div class="result">
					<BuilderModal
						v-if="displayedItemId == itemId"
						:close-action="{
							desc: 'Close',
							fn: () => (displayedItemId = null),
						}"
						icon="find_in_page"
						modal-title="Details"
					>
						<div class="detailsModalContent">
							<div>
								<h2>Result</h2>
								<p>
									The value resulting of the execution of this
									block. This value is added to the execution
									environment of the direct dependents of this
									block. There, it's accessible via @{result}.
								</p>
								<div class="data" data-automation-key="result">
									<SharedJsonViewer
										v-if="item?.result"
										:data="item.result"
										:initial-depth="1"
										class="data"
									/>
									<div v-else class="nothing">No result.</div>
								</div>
							</div>
							<div>
								<h2>Execution environment</h2>
								<p>
									The following values were made available to
									this block during execution time. These
									values are accessible via the same template
									syntax i.e. @{my_var}, as state elements.
								</p>
								<div class="data">
									<SharedJsonViewer
										v-if="item?.executionEnvironment"
										:data="item.executionEnvironment"
										:initial-depth="1"
										class="data"
									/>
									<div v-else class="nothing">
										Empty execution environment.
									</div>
								</div>
							</div>
							<div>
								<h2>Return value</h2>
								<p>
									The value being returned, which is used to
									determine the result of 'Run workflow'
									blocks and 'Chat completion' tool calls.
								</p>
								<div
									class="data"
									data-automation-key="return-value"
								>
									<SharedJsonViewer
										v-if="item?.returnValue"
										:data="item.returnValue"
										:initial-depth="1"
										class="data"
									/>
									<template v-else>
										No return value.
									</template>
								</div>
							</div>
						</div>
					</BuilderModal>
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
						<i class="material-symbols-outlined">find_in_page</i>
						Details
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
	</div>
</template>

<script setup lang="ts">
import { marked } from "marked";
import injectionKeys from "@/injectionKeys";
import { WorkflowExecutionLog } from "../builderManager";
import { computed, inject, nextTick, ref } from "vue";
import { Component, WriterComponentDefinition } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import SharedJsonViewer from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderModal from "../BuilderModal.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

const props = defineProps<{
	executionLog: WorkflowExecutionLog;
}>();
const displayedItemId = ref<number | null>(null);

type EnrichedExecutionLog = WorkflowExecutionLog & {
	summary: {
		component?: Component;
		componentDef?: WriterComponentDefinition;
	}[];
};

const enrichedExecutionLog = computed(() => {
	const eLog: EnrichedExecutionLog = {
		summary: [
			...props.executionLog.summary.map((item) => ({
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
	wfbm.setMode("workflows");
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

.BuilderLogWorkflowExecution {
	display: flex;
	flex-direction: column;
	margin-left: 20px;
}

.row {
	display: grid;
	grid-template-columns: 20px 1fr;
	grid-template-rows: calc(50% + 5px) 1fr;
}

.row .marker {
	border-color: var(--builderSeparatorColor);
	border-style: solid;
	border-width: 0;
}

.row:not(:last-of-type) .marker.bottom {
	border-left-width: 1px;
}

.row .marker.top {
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	border-left-width: 1px;
	border-bottom-width: 1px;
}

.row .marker.bottom {
	grid-column: 1 / 2;
	grid-row: 2 / 3;
}

.item {
	margin-top: 10px;
	grid-column: 2 / 3;
	grid-row: 1 / 3;
	display: grid;
	grid-template-columns: 1fr 0.5fr 120px 80px;
	grid-template-rows: 1fr auto;
	column-gap: 16px;
	align-items: center;
	padding: 8px;
	border-radius: 6px;
	border: 1px solid var(--builderSeparatorColor);
}

.item .name {
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	display: flex;
	gap: 8px;
	align-items: center;
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
}

.detailsModalContent {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.detailsModalContent div:not(:first-of-type) {
	padding-top: 16px;
	border-top: 1px solid var(--builderSeparatorColor);
}

.detailsModalContent .data {
	background-color: var(--builderSubtleSeparatorColor);
	padding: 8px;
	border-radius: 8px;
	margin-top: 8px;
	font-size: 14px;
	overflow-x: auto;
}

.markdown :deep(code) {
	font-family: monospace;
	font-size: 13px;
	background-color: rgba(0, 0, 0, 0.05);
	padding: 2px;
}
</style>
