<template>
	<div class="BuilderLogWorkflowExecution">
		<div
			v-for="(item, itemId) in enrichedExecutionLog"
			:key="itemId"
			class="row"
		>
			<div class="marker top"></div>
			<div class="marker bottom"></div>
			<div class="item">
				<div
					class="name"
					tabindex="0"
					@keydown.enter="selectBlock(item.componentId)"
					@click="selectBlock(item.componentId)"
				>
					{{ item.componentDef.name }}
				</div>
				<div class="outcome">
					<div
						class="ball"
						:class="item.componentDef.outs[item.outcome].style"
					></div>
					{{
						item.componentDef.outs[item.outcome]?.name ??
						item.outcome
					}}
				</div>
				<div class="result">
					<BuilderModal
						v-if="displayedResult !== null"
						:close-action="{
							desc: 'Close',
							fn: () => (displayedResult = null),
						}"
						icon="find_in_page"
						modal-title="Result"
					>
						<BaseJsonViewer
							v-if="displayedResult"
							:data="displayedResult"
							:initial-depth="1"
						/>
					</BuilderModal>
					<WdsButton
						v-if="item.result"
						variant="secondary"
						size="small"
						@click="() => (displayedResult = item.result)"
					>
						<i class="material-symbols-outlined">find_in_page</i>
						View result
					</WdsButton>
				</div>
				<div class="time">
					{{ formatExecutionTime(item.executionTimeInSeconds) }}
				</div>
			</div>
		</div>
		<!-- <table>
			<tr>
				<th></th>
				<th>Outcome</th>
				<th>Time</th>
			</tr>
			<tr>
				<td class="name">
					
				</td>
				<td>
					
				</td>
				<td></td>
			</tr>
		</table> -->
	</div>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { WorkflowExecutionLog } from "./builderManager";
import { computed, inject, nextTick, ref } from "vue";
import { Component, WriterComponentDefinition } from "@/writerTypes";
import { useComponentActions } from "./useComponentActions";
import BaseJsonViewer from "@/components/core/base/BaseJsonViewer.vue";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderModal from "./BuilderModal.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

const props = defineProps<{
	executionLog: WorkflowExecutionLog;
}>();
const displayedResult = ref<any>(null);

type EnrichedExecutionLog = WorkflowExecutionLog &
	{
		component?: Component;
		componentDef?: WriterComponentDefinition;
	}[];

const enrichedExecutionLog = computed(() => {
	const eLog: EnrichedExecutionLog = [
		...props.executionLog.map((item) => ({
			...item,
			component: wf.getComponentById(item.componentId),
			componentDef: wf.getComponentById(item.componentId)
				? wf.getComponentDefinition(
						wf.getComponentById(item.componentId).type,
					)
				: undefined,
		})),
	];
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
@import "./sharedStyles.css";

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
	grid-template-columns: 1fr 1fr 1fr 80px;
	grid-template-rows: 1fr;
	align-items: center;
	padding: 8px;
	border-radius: 6px;
	border: 1px solid var(--builderSeparatorColor);
}

.item .name {
	grid-column: 1 / 2;
	grid-row: 1 / 2;
	cursor: pointer;
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
	background: #3bdcab;
}

.item .outcome .ball.error {
	background: #ff643c;
}

.item .outcome .ball.dynamic {
	background: #a95ef8;
}

.item .result {
	grid-column: 3 / 4;
	grid-row: 1 / 2;
}

.item .time {
	grid-column: 4 / 5;
	grid-row: 1 / 2;
}
</style>
