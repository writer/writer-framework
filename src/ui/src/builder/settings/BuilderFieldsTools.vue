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
					size="small"
					class="delete"
					@click.stop="deleteTool(toolName)"
				>
					<i class="material-symbols-outlined">delete</i>
				</WdsButton>
			</div>
		</div>

		<WdsButton size="small" @click="resetAndShowToolFormModal">
			<i class="material-symbols-outlined">add</i>
			Add tool</WdsButton
		>
		<BuilderModal
			v-if="toolForm.isShown"
			:close-action="customHandlerModalCloseAction"
			icon="add"
			modal-title="Add tool"
		>
			<div class="addToolForm">
				<WdsFieldWrapper label="Tool type">
					<WdsDropdownInput v-model="toolForm.type">
						<option value="function">Function</option>
						<option value="graph">Knowledge graph</option>
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
						variant="minimal"
						language="json"
					></BuilderEmbeddedCodeEditor>
				</WdsFieldWrapper>
				<WdsFieldWrapper
					v-if="toolForm.type == 'graph'"
					label="Graph id(s)"
					hint="Specify the id of the knowledge graph you want to use. If multiple, separate the ids using commas."
				>
					<WdsTextareaInput
						v-model="toolForm.graphIds"
					></WdsTextareaInput>
				</WdsFieldWrapper>
			</div>
			<div class="addToolFormActions">
				<WdsButton @click="saveToolForm">Save</WdsButton>
			</div>
		</BuilderModal>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, ref, defineAsyncComponent } from "vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderModal, { ModalAction } from "../BuilderModal.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import WdsDropdownInput from "@/wds/WdsDropdownInput.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";

const BuilderEmbeddedCodeEditor = defineAsyncComponent(
	() => import("../BuilderEmbeddedCodeEditor.vue"),
);

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

type Tool = FunctionTool | GraphTool;

type ToolForm = {
	isShown: boolean;
	type: "function" | "graph";
	originalName?: string;
	name: string;
	code: string;
	graphIds: string;
};

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const initFunctionToolCode = `
{
	"description": "Gets info for an employee, given an employee id",
    "parameters": {
      "id": {"type": "string", "description": "Id of the employee"}
    }
}
`.trim();

const toolFormInitValue = {
	isShown: false,
	type: "function" as "function" | "graph",
	name: "new_tool",
	code: initFunctionToolCode,
	graphIds: "6029b226-1ee0-4239-a1b0-cdeebfa3ad5a",
};

const toolForm = ref<ToolForm>(toolFormInitValue);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const tools = computed<Record<string, Tool>>(() => {
	let value = {};
	try {
		value = JSON.parse(component.value.content[fieldKey.value]);
	} catch {
		value = {};
	}
	return value;
});

function resetAndShowToolFormModal() {
	toolForm.value = {
		...toolFormInitValue,
		isShown: true,
	};
}

function getToolFromForm(): Tool {
	const { type, code, graphIds } = toolForm.value;
	if (type == "function") {
		return {
			...JSON.parse(code),
			type,
		};
	}
	if (type == "graph") {
		const graphArr = graphIds.split(",").map((gId) => gId.trim());
		return {
			type,
			graph_ids: graphArr,
		};
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
	const newFieldValue = JSON.stringify({
		...tools.value,
		...(toolForm.value.originalName
			? { [toolForm.value.originalName]: undefined }
			: {}),
		[toolForm.value.name]: toolFromForm,
	});
	setContentValue(component.value.id, fieldKey.value, newFieldValue);
	toolForm.value.isShown = false;
}

function getFormFromToolEntry(toolName: string, tool: Tool): ToolForm {
	const { type } = tool;
	if (type == "function") {
		return {
			isShown: true,
			type: "function",
			originalName: toolName,
			name: toolName,
			graphIds: "",
			code: JSON.stringify(tool, undefined, 2),
		};
	}
	if (type == "graph") {
		return {
			isShown: true,
			type: "graph",
			originalName: toolName,
			name: toolName,
			graphIds: tool.graph_ids?.join(","),
			code: "",
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
	const newFieldValue = JSON.stringify({
		...tools.value,
		[toolName]: undefined,
	});
	setContentValue(component.value.id, fieldKey.value, newFieldValue);
}

const customHandlerModalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		toolForm.value.isShown = false;
	},
};
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
	display: none;
}

.tool:hover .delete {
	display: unset;
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

.addToolFormActions {
	margin-top: 16px;
}
</style>
