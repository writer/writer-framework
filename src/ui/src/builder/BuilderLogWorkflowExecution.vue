<template>
	<div class="BuilderLogWorkflowExecution">
		<table>
			<tr>
				<th></th>
				<th>Outcome</th>
				<th>Time</th>
			</tr>
			<tr v-for="(entry, entryId) in enrichedExecutionLog" :key="entryId">
				<td class="name" @click="selectBlock(entry.componentId)">
					{{ entry.componentDef.name }}
				</td>
				<td>
					{{
						entry.componentDef.outs[entry.outcome]?.name ??
						entry.outcome
					}}
				</td>
				<td>{{ formatExecutionTime(entry.executionTimeInSeconds) }}</td>
			</tr>
		</table>
	</div>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { WorkflowExecutionLog } from "./builderManager";
import { computed, inject, nextTick } from "vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "./useComponentActions";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

const props = defineProps<{
	executionLog: WorkflowExecutionLog;
}>();

const enrichedExecutionLog = computed(() => {
	const elog = [...props.executionLog];
	elog.map((e) => {
		e.component = wf.getComponentById(e.componentId);
		if (!e.component) return;
		e.componentDef = wf.getComponentDefinition(e.component.type);
	});
	return elog;
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
}

table {
	border-collapse: collapse;
	font-size: 12px;
}

th {
	font-weight: bold;
	text-align: left;
}

th,
td {
	border: 1px solid var(--builderSeparatorColor);
	margin: 0;
	padding: 4px;
}

td.name {
	cursor: pointer;
}

td.name:hover {
	background: var(--builderSubtleSeparatorColor);
}
</style>
