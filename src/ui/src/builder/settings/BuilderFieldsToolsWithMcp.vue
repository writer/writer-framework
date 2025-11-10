<template>
	<div
		class="BuilderFieldsToolsWithMcp colorTransformer"
		:data-automation-key="props.fieldKey"
	>
		<div class="availableMcpTools">
			<div class="sectionHeader">
				<div class="sectionTitle">Available MCP Tools</div>
				<WdsButton
					size="small"
					variant="secondary"
					:loading="mcpToolsLoading"
					@click="loadMcpTools()"
				>
					<WdsIcon name="refresh-cw" />
					Refresh
				</WdsButton>
			</div>
			<div v-if="mcpToolsError" class="errorState">
				Error loading MCP tools: {{ mcpToolsError.message }}
				<br />
				<small>Check console for details</small>
			</div>
			<div
				v-else-if="mcpToolsLoading && mcpToolsData.length === 0"
				class="loadingState"
			>
				<div v-for="index in 3" :key="index" class="loadingSkeleton">
					<WdsSkeletonLoader
						style="width: 200px; margin-bottom: 8px"
					/>
					<WdsSkeletonLoader style="width: 150px" />
				</div>
			</div>
			<div v-else-if="mcpToolsData.length === 0" class="emptyState">
				No MCP tools available
				<br />
				<small
					>Make sure you have connected MCP applications with enabled
					functions</small
				>
			</div>
			<div
				v-else
				class="mcpToolsList"
				:class="{ loading: mcpToolsLoading }"
			>
				<div
					v-for="(group, appName) in groupedTools"
					:key="appName"
					class="mcpAppGroup"
					:class="{ expanded: expandedApps.has(appName) }"
				>
					<div
						class="mcpAppHeader"
						:class="{ expanded: expandedApps.has(appName) }"
						@click="toggleApp(appName)"
					>
						<div class="iconContainer">
							<WdsIcon
								:name="
									expandedApps.has(appName) ? 'minus' : 'plus'
								"
								class="expandIcon"
							/>
						</div>
						<img
							v-if="group.logo"
							:src="group.logo"
							:alt="`${appName} logo`"
							class="appLogo"
						/>
						<span class="appName">{{ appName }}</span>
						<span
							v-if="selectedCountsByApp[appName] > 0"
							class="selectedCount"
						>
							{{ selectedCountsByApp[appName] }} selected
						</span>
					</div>
					<div
						v-if="expandedApps.has(appName)"
						class="mcpFunctionsList"
					>
						<div
							v-for="tool in group.functions"
							:key="`${tool.appId}-${tool.functionName}`"
							class="mcpFunctionItem"
							:data-writer-tooltip="tool.function?.description"
							data-writer-tooltip-placement="left"
						>
							<WdsCheckbox
								class="functionCheckbox"
								:model-value="isToolSelected(tool)"
								@update:model-value="toggleTool(tool, $event)"
							/>
							<div
								class="functionInfo"
								@click="toggleTool(tool, !isToolSelected(tool))"
							>
								<div class="functionName">
									{{ tool.functionName }}
								</div>
								<div
									v-if="tool.function?.description"
									class="functionDescription"
								>
									{{ tool.function.description }}
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, ref, toRef } from "vue";
import { Component } from "@/writerTypes";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import WdsSkeletonLoader from "@/wds/WdsSkeletonLoader.vue";
import injectionKeys from "@/injectionKeys";
import { useWriterApi } from "@/composables/useWriterApi";
import type { WriterApiMcpTool } from "@/writerApi";

type FunctionTool = {
	type: "function";
	description: string;
	parameters: Record<
		string,
		{
			type: string;
			description: string;
		}
	>;
};

type GraphTool = {
	type: "graph";
	graph_ids: string[];
};

type WebSearchTool = {
	type: "web_search";
	include_domains?: string[];
	exclude_domains?: string[];
	include_raw_content?: boolean;
};

type McpToolFunction = {
	description?: string;
	parameters?: Record<string, unknown>;
	name?: string;
	[key: string]: unknown;
};

type McpToolType = {
	type: "mcp";
	appId: string;
	functionName: string;
	function: McpToolFunction;
};

type Tool = FunctionTool | GraphTool | WebSearchTool | McpToolType;

const wf = inject(injectionKeys.core);

const { writerApi } = useWriterApi();

const mcpToolsData = ref<WriterApiMcpTool[]>([]);
const mcpToolsLoading = ref(false);
const mcpToolsError = ref<Error | undefined>(undefined);
const expandedApps = ref<Set<string>>(new Set());

type GroupedTool = {
	functions: WriterApiMcpTool[];
	logo?: string;
};

const groupedTools = computed(() => {
	const grouped: Record<string, GroupedTool> = {};

	for (const tool of mcpToolsData.value) {
		const appName = tool.appName || "Unknown App";
		if (!grouped[appName]) {
			grouped[appName] = {
				functions: [],
				logo: tool.connector?.logo,
			};
		}
		grouped[appName].functions.push(tool);
	}
	return grouped;
});

const selectedCountsByApp = computed(() => {
	const counts: Record<string, number> = {};
	for (const [appName, group] of Object.entries(groupedTools.value)) {
		counts[appName] = group.functions.filter((tool) =>
			isToolSelected(tool),
		).length;
	}
	return counts;
});

function toggleApp(appName: string) {
	if (expandedApps.value.has(appName)) {
		expandedApps.value.delete(appName);
	} else {
		expandedApps.value.add(appName);
	}
}

function normalizeToolName(tool: WriterApiMcpTool): string {
	return `${tool.appName}_${tool.functionName}`.replace(
		/[^a-zA-Z0-9_]/g,
		"_",
	);
}

function isToolSelected(tool: WriterApiMcpTool): boolean {
	return normalizeToolName(tool) in tools.value;
}

function toggleTool(tool: WriterApiMcpTool, checked: boolean) {
	const toolName = normalizeToolName(tool);

	if (checked) {
		const mcpTool: McpToolType = {
			type: "mcp",
			appId: tool.appId,
			functionName: tool.functionName,
			function: tool.function,
		};
		fieldViewModel.value = JSON.stringify({
			...tools.value,
			[toolName]: mcpTool,
		});
	} else {
		const updatedTools = { ...tools.value };
		delete updatedTools[toolName];
		fieldViewModel.value = JSON.stringify(updatedTools);
	}
}

async function loadMcpTools() {
	const orgId = wf.writerOrgId.value || 1;

	if (!orgId) {
		const error = new Error("No organization ID available");
		mcpToolsError.value = error;
		return;
	}

	mcpToolsLoading.value = true;
	mcpToolsError.value = undefined;

	try {
		const appId = wf.writerAppId.value;
		mcpToolsData.value = await writerApi.fetchMcpTools(orgId, appId);
	} catch (e) {
		const error = e instanceof Error ? e : new Error(String(e));
		mcpToolsError.value = error;
		mcpToolsData.value = [];
	} finally {
		mcpToolsLoading.value = false;
	}
}

onMounted(() => {
	loadMcpTools();
});

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

const tools = computed<Record<string, Tool>>(() => {
	try {
		return JSON.parse(fieldViewModel.value);
	} catch {
		return {};
	}
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsToolsWithMcp {
	--separatorColor: var(--builderSeparatorColor);
	--intensifiedButtonColor: red;
}

.availableMcpTools {
	margin-bottom: 16px;
}

.sectionHeader {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12px;
}

.sectionTitle {
	font-weight: 600;
	color: var(--builderPrimaryTextColor);
}

.loadingState {
	padding: 12px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.loadingSkeleton {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.errorState,
.emptyState {
	padding: 12px;
	text-align: center;
	color: var(--builderSecondaryTextColor);
	font-size: 0.875rem;
}

.errorState {
	color: var(--builderErrorColor);
}

.mcpToolsList {
	display: flex;
	flex-direction: column;
	gap: 4px;
	position: relative;
}

.mcpToolsList.loading {
	opacity: 0.6;
	pointer-events: none;
}

.mcpAppGroup {
	border-radius: 8px;
	overflow: hidden;
	margin-bottom: 4px;
	transition: background-color 0.2s;
}

.mcpAppGroup.expanded {
	background: var(--builderSubtleSeparatorColor);
}

.mcpAppHeader {
	display: flex;
	align-items: center;
	padding: 12px 12px 12px 0;
	cursor: pointer;
	transition: background-color 0.2s;
	background-color: transparent;
}

.iconContainer {
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 5px 0 8px;
}

.mcpAppHeader:hover {
	background: var(--builderSubtleSeparatorColor);
}

.mcpAppGroup.expanded .mcpAppHeader {
	background: var(--builderSubtleSeparatorColor);
}

.mcpAppGroup.expanded .mcpAppHeader:hover {
	background: var(--builderSubtleSeparatorColor);
}

.mcpAppHeader.expanded {
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.expandIcon {
	color: var(--builderAccentColor);
	margin: 0 5px;
	flex-shrink: 0;
	width: 14px;
	height: 14px;
}

.appLogo {
	width: 20px;
	height: 20px;
	margin-right: 8px;
	object-fit: contain;
	flex-shrink: 0;
}

.appName {
	font-weight: 600;
	color: var(--builderPrimaryTextColor);
	flex: 1;
}

.selectedCount {
	font-size: 0.75rem;
	color: var(--builderSecondaryTextColor);
	font-weight: 400;
	margin-left: 8px;
}

.mcpFunctionsList {
	display: flex;
	flex-direction: column;
}

.mcpFunctionItem {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 12px;
	padding-left: 14px;
	padding-right: 24px;
	transition: background-color 0.2s;
	border-top: 1px solid var(--builderSeparatorColor);
	width: 100%;
	box-sizing: border-box;
}

.mcpFunctionItem:first-child {
	border-top: none;
}

.mcpFunctionItem:hover {
	background: var(--builderSubtleSeparatorColor);
}

.functionCheckbox {
	flex-shrink: 0;
}

.functionInfo {
	flex: 1 1 auto;
	cursor: pointer;
	min-width: 0;
	max-width: 100%;
	overflow: hidden;
}

.functionName {
	font-weight: 500;
	margin-bottom: 4px;
	color: var(--builderPrimaryTextColor);
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	max-width: 100%;
}

.functionDescription {
	font-size: 0.875rem;
	color: var(--builderSecondaryTextColor);
	line-height: 1.4;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	max-width: 100%;
}

.mcpFunctionItem .addIcon {
	color: var(--builderAccentColor);
	margin-left: 12px;
	flex-shrink: 0;
}
</style>
