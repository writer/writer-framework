<template>
	<div
		class="BuilderFieldsTools colorTransformer"
		:data-automation-key="props.fieldKey"
	>
		<div class="tools">
			<div
				v-for="(tool, toolName) in tools"
				:key="toolName"
				class="tool"
				@click="editTool(toolName)"
			>
				<div class="toolName">{{ toolName }}</div>
				<button class="delete" @click.stop="deleteTool(toolName)">
					<i class="material-symbols-outlined">delete</i>
				</button>
			</div>
		</div>

		<WdsButton
			variant="builder"
			size="small"
			@click="resetAndShowToolFormModal"
		>
			<i class="material-symbols-outlined">add</i>
			Add tool</WdsButton
		>
		<BuilderModal
			v-if="toolForm.isShown"
			:close-action="customHandlerModalCloseAction"
			icon="add"
			modal-title="Add tool"
		>
			<WdsDropdownInput v-model="toolForm.type">
				<option value="function">Function</option>
				<option value="graph">Knowledge graph</option>
			</WdsDropdownInput>
			<WdsTextInput v-model="toolForm.name"></WdsTextInput>
			<template v-if="toolForm.type == 'function'">
				<BuilderEmbeddedCodeEditor
					v-model="toolForm.code"
				></BuilderEmbeddedCodeEditor>
			</template>
			<template v-if="toolForm.type == 'graph'">
				<WdsTextInput v-model="toolForm.graphId"></WdsTextInput>
			</template>
			<div>
				<WdsButton variant="builder" @click="saveToolForm"
					>Save</WdsButton
				>
			</div>
		</BuilderModal>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, ref, Ref, ComputedRef } from "vue";
import { Component, FieldControl } from "@/writerTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import WdsButton from "@/wds/WdsButton.vue";
import BuilderModal, { ModalAction } from "./BuilderModal.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsDropdownInput from "@/wds/WdsDropdownInput.vue";
import BuilderEmbeddedCodeEditor from "./BuilderEmbeddedCodeEditor.vue";

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
	name: string;
	code: string;
	graphId: string;
};

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const initFunctionToolCode = `
{
	"description": "An example tool",
	"parameters": {
		"city": string
	}
}
`.trim();

const toolFormInitValue = {
	isShown: false,
	type: "function" as "function" | "graph",
	name: "new_tool",
	code: initFunctionToolCode,
	graphId: "999-999",
};

const toolForm: Ref<ToolForm> = ref(toolFormInitValue);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const tools: ComputedRef<Record<string, Tool>> = computed(() => {
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
	const { type, code, graphId } = toolForm.value;
	if (type == "function") {
		return {
			...JSON.parse(code),
			type,
		};
	}
	if (type == "graph") {
		return {
			type,
			graph_ids: [graphId],
		};
	}
	throw "Unexpected tool type.";
}

function validateToolForm(form: ToolForm): string[] {
	let errors = [];
	const { name } = form;
	if (!name) {
		errors.push("The name cannot be empty.");
	}
	if (Object.keys(tools.value).includes(name)) {
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
			name: toolName,
			graphId: "",
			code: JSON.stringify(tool, undefined, 2),
		};
	}
	if (type == "graph") {
		return {
			isShown: true,
			type: "graph",
			name: toolName,
			graphId: tool.graph_ids?.[0],
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

<style>
@import "@/renderer/colorTransformations.css";

.BuilderFieldsTool {
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
	background: var(--builderBackgroundColor);
	padding: 2px 4px 2px 4px;
	font-size: 1.1rem;
}

.tool:hover .delete {
	display: block;
}

.addToolTextarea {
	font-family: monospace;
}
</style>

<style scoped>
@import "./sharedStyles.css";
</style>
