<template>
	<div
		class="BuilderFieldsTools colorTransformer"
		:data-automation-key="props.fieldKey"
	>
		<div class="tools">
			<div
				v-for="(_tool, toolName) in tools"
				:key="toolName"
				class="tool"
				@click="editTool(toolName)"
			>
				<div class="toolName">{{ toolName }}</div>
				<WdsButton
					variant="primary"
					size="smallIcon"
					class="delete"
					@click.stop="deleteTool(toolName)"
				>
					<WdsIcon name="trash-2" />
				</WdsButton>
			</div>
		</div>

		<WdsButton size="small" @click="resetAndShowToolFormModal">
			<WdsIcon name="plus" />
			Add tool
		</WdsButton>
		<WdsModal
			v-if="toolForm.isShown"
			:actions="modalActions"
			title="Add tool"
			allow-overflow
		>
			<div class="addToolForm">
				<WdsFieldWrapper label="Tool type">
					<WdsDropdownInput v-model="toolForm.type">
						<option value="function">Function</option>
						<option value="graph">Knowledge graph</option>
						<option value="web_search">Web search</option>
					</WdsDropdownInput>
				</WdsFieldWrapper>
				<WdsFieldWrapper label="Tool name">
					<WdsTextInput v-model="toolForm.name"></WdsTextInput>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					v-if="toolForm.type == 'function'"
					:frame-slot="true"
					label="Function tool definition"
				>
					<BuilderEmbeddedCodeEditor
						v-model="toolForm.code"
						class="addToolForm__codeEditor"
						variant="minimal"
						language="json"
					></BuilderEmbeddedCodeEditor>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					v-if="toolForm.type == 'graph'"
					v-model:is-binding-enabled="toolForm.binding"
					label="Graph id(s)"
					hint="Specify the id of the knowledge graph you want to use. If multiple, separate the ids using commas."
					is-binding-button-shown
				>
					<BuilderTemplateInput
						v-if="toolForm.binding"
						type="state"
						:value="graphIdBinding"
						@update:value="graphIdBinding = $event"
					/>
					<BuilderGraphSelect
						v-else
						v-model="graphIds"
						enable-multi-selection
					/>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					v-if="toolForm.type == 'web_search'"
					label="Include domains (optional)"
					hint="Comma-separated list of domains to search within (e.g., wikipedia.org, docs.python.org)"
				>
					<WdsTextInput
						v-model="toolForm.includeDomains"
						placeholder="domain1.com, domain2.org"
					></WdsTextInput>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					v-if="toolForm.type == 'web_search'"
					label="Exclude domains (optional)"
					hint="Comma-separated list of domains to exclude from results"
				>
					<WdsTextInput
						v-model="toolForm.excludeDomains"
						placeholder="spam.com, ads.net"
					></WdsTextInput>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					v-if="toolForm.type == 'web_search'"
					label="Include raw content"
					hint="Include full page content in search results"
				>
					<WdsCheckbox
						v-model="toolForm.includeRawContent"
						label="Include raw content"
					></WdsCheckbox>
				</WdsFieldWrapper>
			</div>
		</WdsModal>
	</div>
</template>

<script setup lang="ts">
import { computed, ref, toRef } from "vue";
import { Component } from "@/writerTypes";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsDropdownInput from "@/wds/WdsDropdownInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsCheckbox from "@/wds/WdsCheckbox.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";
import { TEMPLATE_REGEX } from "@/renderer/useEvaluator";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";

const BuilderGraphSelect = defineAsyncComponentWithLoader({
	loader: () => import("../BuilderGraphSelect.vue"),
});

const BuilderEmbeddedCodeEditor = defineAsyncComponentWithLoader({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
});

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

type Tool = FunctionTool | GraphTool | WebSearchTool;

type ToolForm = {
	isShown: boolean;
	type: "function" | "graph" | "web_search";
	originalName?: string;
	name: string;
	code: string;
	graphIds: string;
	binding: boolean;
	includeDomains: string;
	excludeDomains: string;
	includeRawContent: boolean;
};

const initFunctionToolCode = `
{
	"description": "Gets info for an employee, given an employee id",
    "parameters": {
      "id": {"type": "string", "description": "Id of the employee"}
    }
}
`.trim();

const toolFormInitValue: ToolForm = {
	isShown: false,
	type: "function" as "function" | "graph" | "web_search",
	name: "new_tool",
	code: initFunctionToolCode,
	graphIds: "",
	binding: false,
	includeDomains: "",
	excludeDomains: "",
	includeRawContent: false,
};

const toolForm = ref<ToolForm>(toolFormInitValue);

const saveDisabled = computed(() => {
	switch (toolForm.value.type) {
		case "function":
			return !toolForm.value.code;
		case "graph":
			return !toolForm.value.graphIds;
		case "web_search":
			return false; // Web search tool has no required fields
		default:
			return true;
	}
});

const graphIds = computed<string[]>({
	get: () =>
		toolForm.value.graphIds.split(",").filter((i) => !i.startsWith("@{")),
	set(ids) {
		toolForm.value = { ...toolForm.value, graphIds: ids.join(",") };
	},
});

const graphIdBinding = computed<string>({
	get: () => {
		const match = TEMPLATE_REGEX.exec(toolForm.value.graphIds);
		return match?.[1] ?? "";
	},
	set(binding) {
		toolForm.value = { ...toolForm.value, graphIds: `@{${binding}}` };
	},
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

function resetAndShowToolFormModal() {
	toolForm.value = {
		...toolFormInitValue,
		isShown: true,
	};
}

function getToolFromForm(): Tool {
	const {
		type,
		code,
		graphIds,
		includeDomains,
		excludeDomains,
		includeRawContent,
	} = toolForm.value;
	if (type == "function") {
		return {
			...JSON.parse(code),
			type,
		};
	}
	if (type == "graph") {
		const graphArr = graphIds.split(",").map((gId) => gId.trim());
		return { type, graph_ids: graphArr };
	}
	if (type == "web_search") {
		const tool: WebSearchTool = { type };
		if (includeDomains.trim()) {
			tool.include_domains = includeDomains
				.split(",")
				.map((d) => d.trim())
				.filter((d) => d);
		}
		if (excludeDomains.trim()) {
			tool.exclude_domains = excludeDomains
				.split(",")
				.map((d) => d.trim())
				.filter((d) => d);
		}
		if (includeRawContent) {
			tool.include_raw_content = includeRawContent;
		}
		return tool;
	}
	throw "Unexpected tool type.";
}

function validateToolForm(form: ToolForm): string[] {
	let errors = [];
	const { originalName, name } = form;
	if (!name) {
		errors.push("The name cannot be empty.");
	}
	if (
		Object.keys(tools.value).includes(name) &&
		!(originalName || originalName == name)
	) {
		errors.push("An existing tool with the specified name already exists.");
	}
	return errors;
}

function saveToolForm() {
	const formErrors = validateToolForm(toolForm.value);
	if (formErrors.length > 0) {
		formErrors.forEach(alert);
		return;
	}
	let toolFromForm: ReturnType<typeof getToolFromForm>;
	try {
		toolFromForm = getToolFromForm();
	} catch {
		alert("Incorrect tool definition");
		return;
	}

	fieldViewModel.value = JSON.stringify({
		...tools.value,
		...(toolForm.value.originalName
			? { [toolForm.value.originalName]: undefined }
			: {}),
		[toolForm.value.name]: toolFromForm,
	});

	toolForm.value.isShown = false;
}

function getFormFromToolEntry(toolName: string, tool: Tool): ToolForm {
	const { type } = tool;
	if (type == "function") {
		return {
			isShown: true,
			type: "function",
			binding: false,
			originalName: toolName,
			name: toolName,
			graphIds: "",
			code: JSON.stringify(tool, undefined, 2),
			includeDomains: "",
			excludeDomains: "",
			includeRawContent: false,
		};
	}
	if (type == "graph") {
		const binding = TEMPLATE_REGEX.test(tool.graph_ids?.at(0) ?? "");
		return {
			isShown: true,
			type: "graph",
			originalName: toolName,
			name: toolName,
			binding,
			graphIds: tool.graph_ids?.join(",") ?? "",
			code: "",
			includeDomains: "",
			excludeDomains: "",
			includeRawContent: false,
		};
	}
	if (type == "web_search") {
		return {
			isShown: true,
			type: "web_search",
			originalName: toolName,
			name: toolName,
			graphIds: "",
			binding: false,
			code: "",
			includeDomains: tool.include_domains?.join(", ") ?? "",
			excludeDomains: tool.exclude_domains?.join(", ") ?? "",
			includeRawContent: tool.include_raw_content ?? false,
		};
	}
	throw "Unexpected tool type;";
}

function editTool(toolName: string) {
	const tool = tools.value?.[toolName];
	if (!tool) return;
	toolForm.value = getFormFromToolEntry(toolName, tool);
}

function deleteTool(toolName: string) {
	fieldViewModel.value = JSON.stringify({
		...tools.value,
		[toolName]: undefined,
	});
}

const modalActions = computed<ModalAction[]>(() => [
	{
		desc: "cancel",
		fn: () => (toolForm.value.isShown = false),
	},
	{
		desc: "Save",
		disabled: saveDisabled.value,
		fn: saveToolForm,
	},
]);
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsTools {
	--separatorColor: var(--builderSeparatorColor);
	--intensifiedButtonColor: red;
}

.tools {
	margin-bottom: 8px;
}

.tool {
	display: flex;
	align-items: center;
	min-height: 38px;
	padding-top: 4px;
	margin-top: 4px;
	cursor: pointer;
}

.tool:not(:first-of-type) {
	border-top: 1px solid var(--builderSeparatorColor);
}

.tool .toolName {
	flex: 1 0 auto;
}

.tool .delete {
	visibility: hidden;
}

.tool:hover .delete {
	visibility: visible;
}

.addToolForm {
	display: grid;
	grid-template-columns: 1fr 1fr;
	grid-template-rows: auto;
	gap: 16px;
}

.addToolForm > :nth-child(n + 3) {
	grid-column: span 2;
}

.addToolForm__codeEditor {
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	overflow: hidden;
}
</style>
