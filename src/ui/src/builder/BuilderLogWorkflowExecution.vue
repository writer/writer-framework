<template>
	<div class="BuilderLogWorkflowExecution">
		<table>
			<tr>
				<th></th>
				<th>Outcome</th>
				<th>Time</th>
			</tr>
			<tr v-for="(entry, entryId) in enrichedExecutionLog" :key="entryId">
				<td @click="selectBlock(entry.componentId)">
					{{ entry.componentDef.name }}
				</td>
				<td>
					{{
						entry.componentDef.outs[entry.outcome]?.name ??
						entry.outcome
					}}
				</td>
				<td>1s</td>
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
</style>
