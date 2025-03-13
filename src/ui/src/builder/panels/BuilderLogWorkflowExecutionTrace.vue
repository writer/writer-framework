<template>
	<div class="BuiderLogWorkflowExecutionTrace">
		<div v-if="trace.length > 0" class="trace">
			<div
				v-for="(entry, entryId) in trace"
				:key="entryId"
				class="traceEntry"
			>
				<div class="type">
					<span v-if="entry.type == 'functionCall'">⚡️</span>
					<span v-if="entry.type == 'reasoning'">🧠</span>
				</div>
				<div class="main">
					<div v-if="entry.thought">
						<strong>Thought.</strong> {{ entry.thought }}
					</div>
					<div v-if="entry.action">
						<strong>Action.</strong> {{ entry.action }}
					</div>
					<div v-if="entry.name">
						{{ entry.name }}
					</div>
					<div v-if="entry.parameters">
						<SharedJsonViewer
							:hide-root="true"
							:data="entry.parameters"
							:initial-depth="1"
							class="data"
						/>
					</div>
				</div>
			</div>
		</div>
		<div class="details">
			<div>
				<h3>Result</h3>
				<p>
					The value resulting of the execution of this block. This
					value is added to the execution environment of the direct
					dependents of this block. There, it's accessible via
					@{result}.
				</p>
				<div class="data" data-automation-key="result">
					<SharedJsonViewer
						v-if="executionItem?.result"
						:data="executionItem.result"
						:initial-depth="1"
						class="data"
					/>
					<div v-else class="nothing">No result.</div>
				</div>
			</div>
			<div>
				<h3>Return value</h3>
				<p>
					The value being returned, which is used to determine the
					result of 'Run workflow' blocks and 'Chat completion' tool
					calls.
				</p>
				<div class="data" data-automation-key="return-value">
					<SharedJsonViewer
						v-if="executionItem?.returnValue"
						:data="executionItem.returnValue"
						:initial-depth="1"
						class="data"
					/>
					<template v-else> No return value. </template>
				</div>
			</div>
		</div>
		<div class="environment">
			<h3>Execution environment</h3>
			<p>
				The following values were made available to this block during
				execution time. These values are accessible via the same
				template syntax i.e. @{my_var}, as state elements.
			</p>
			<div class="data">
				<SharedJsonViewer
					v-if="executionItem?.executionEnvironment"
					:data="executionItem.executionEnvironment"
					:initial-depth="1"
					class="data"
				/>
				<div v-else class="nothing">Empty execution environment.</div>
			</div>
		</div>

		<div class="callStack">
			<h3>Call stack</h3>
			<div
				v-for="(component, componentId) in callStack"
				:key="componentId"
				class="component"
				:class="{
					active: componentId == executionItem.componentId,
				}"
			>
				<div>
					<div class="eyebrow">
						<template
							v-if="componentId == executionItem.componentId"
						>
							This block &middot;
						</template>
						{{
							wf.getComponentDefinition(component?.type)?.name ??
							"Unavailable component"
						}}
						&middot; Id: {{ componentId }}
					</div>
					{{
						component?.["content"]?.["alias"] ??
						wf.getComponentDefinition(component?.type)?.name ??
						"Unavailable component"
					}}
				</div>
				<WdsButton
					v-if="component"
					variant="neutral"
					size="smallIcon"
					data-writer-tooltip="Jump to this block"
					@click="selectBlock(componentId)"
				>
					<i class="material-symbols-outlined">jump_to_element</i>
				</WdsButton>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import injectionKeys from "@/injectionKeys";
import { WorkflowExecutionLog } from "../builderManager";
import { computed, inject, nextTick } from "vue";
import SharedJsonViewer from "@/components/shared/SharedJsonViewer/SharedJsonViewer.vue";
import WdsButton from "@/wds/WdsButton.vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const emit = defineEmits(["closeModal"]);

const { goToComponentParentPage } = useComponentActions(wf, wfbm);

const props = defineProps<{
	executionItem: WorkflowExecutionLog["summary"][number];
}>();

const callStack = computed(() => {
	const callStackArr: Component["id"][] =
		props.executionItem.executionEnvironment?.["call_stack"] ?? [];

	return Object.fromEntries(
		callStackArr.map((cid) => [cid, wf.getComponentById(cid)]),
	);
});

const trace = computed(() => {
	return props.executionItem.executionEnvironment?.["trace"] ?? [];
});

async function selectBlock(componentId: Component["id"]) {
	emit("closeModal");
	wfbm.setMode("workflows");
	await nextTick();
	goToComponentParentPage(componentId);
	await nextTick();
	wfbm.setSelection(componentId, undefined, "log");
}
</script>

<style scoped>
.BuiderLogWorkflowExecutionTrace {
	display: grid;
	grid-template-columns: 1fr 1fr 1fr;
	grid-template-rows: 1fr 1fr;
	gap: 48px;
}

h3 {
	font-size: 20px;
	font-weight: 500;
	line-height: 160%;
}

.details {
	display: flex;
	flex-direction: column;
	gap: 16px;
	flex: 0 0 40%;
}

.details div:not(:first-of-type) {
	padding-top: 16px;
	border-top: 1px solid var(--builderSeparatorColor);
}

.data {
	background-color: var(--builderSubtleSeparatorColor);
	padding: 8px;
	border-radius: 8px;
	margin-top: 8px;
	font-size: 14px;
	overflow-x: auto;
}

.environment {
}

.callStack {
	display: flex;
	flex-direction: column;
	gap: 8px;
	grid-template-columns: 3 / 3;
}

.callStack .component {
	display: flex;
	align-items: center;
	border-radius: 8px;
	padding: 8px;
	border: 1px solid var(--builderSeparatorColor);
}

.callStack .component > div {
	flex: 1 0 auto;
}

.callStack .component .eyebrow {
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
}

.callStack .component.active {
	border-color: var(--builderSelectedColor);
}

.trace {
	display: flex;
	flex-direction: column;
	gap: 8px;
	grid-column-start: 1;
	grid-column-end: 4;
}

.trace .traceEntry {
	display: flex;
	align-items: center;
	border-radius: 8px;
	border: 1px solid var(--builderSeparatorColor);
}

.trace .traceEntry .type {
	flex: 0 0 72px;
	font-size: 20px;
	height: 100%;
	align-items: center;
	display: flex;
	justify-content: center;
	background: var(--builderSubtleSeparatorColor);
}

.trace .traceEntry .main {
	padding: 8px;
}
</style>
