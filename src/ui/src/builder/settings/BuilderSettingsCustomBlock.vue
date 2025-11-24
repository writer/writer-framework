<template>
	<WdsModal
		v-if="isOpen && isCustomBlocksEnabled"
		:actions="modalActions"
		title="Create Custom Block"
		size="wide"
		display-close-button
		@close="handleClose"
	>
		<div class="BuilderSettingsCustomBlock">
			<div class="BuilderSettingsCustomBlock__left">
				<WdsFieldWrapper label="Name" required>
					<WdsTextInput
						v-model="form.name"
						placeholder="e.g., Extract File Text"
						:error="errors.name"
					/>
				</WdsFieldWrapper>

				<WdsFieldWrapper label="Description" required>
					<textarea
						v-model="form.description"
						placeholder="Describe what this block does"
						class="BuilderSettingsCustomBlock__textarea"
						:class="{ 'BuilderSettingsCustomBlock__textarea--error': errors.description }"
					/>
				</WdsFieldWrapper>

				<WdsFieldWrapper
					label="State Inputs (optional)"
					hint="Comma-separated list of state variables this block reads from"
				>
					<WdsTextInput
						v-model="form.stateInputs"
						placeholder="e.g., upload_file_content, user_data"
					/>
				</WdsFieldWrapper>

				<WdsFieldWrapper
					label="State Outputs (optional)"
					hint="Comma-separated list of state variables this block writes to"
				>
					<WdsTextInput
						v-model="form.stateOutputs"
						placeholder="e.g., extracted_text, processed_data"
					/>
				</WdsFieldWrapper>
			</div>

			<div class="BuilderSettingsCustomBlock__right">
				<WdsFieldWrapper label="Code" required :frame-slot="true" class="BuilderSettingsCustomBlock__codeWrapper">
					<BuilderEmbeddedCodeEditor
						:key="`editor-${isOpen}`"
						v-model="form.code"
						class="BuilderSettingsCustomBlock__codeEditor"
						variant="minimal"
						language="python"
						:error="errors.code"
					/>
				</WdsFieldWrapper>
			</div>
		</div>
	</WdsModal>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, inject } from "vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";
import injectionKeys from "@/injectionKeys";
import { useToasts } from "../useToast";

const BuilderEmbeddedCodeEditor = defineAsyncComponentWithLoader({
	loader: () => import("../BuilderEmbeddedCodeEditor.vue"),
});

const wf = inject(injectionKeys.core);
const { pushToast } = useToasts();

const isCustomBlocksEnabled = computed(() => Array.isArray(wf.featureFlags.value) && wf.featureFlags.value.includes("custom_blocks"));

const INIT_CODE = `# State is accessible as a global variable. For example:
state["counter"] = 10

# Other variables from the execution environment are also available:
# result - Result from the execution of the last block
# results - Dictionary with the execution results of each block
# payload - When executing via API or via an UI event with a payload
# logger - logging.Logger object for capturing logs

# To set the output of this block, which will be available via result to the next block:
set_output("a sample result")
`;

const props = defineProps<{
	modelValue: boolean;
}>();

const emit = defineEmits<{
	"update:modelValue": [value: boolean];
}>();

const isOpen = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
});

const form = ref({
	name: "",
	description: "",
	code: INIT_CODE,
	stateInputs: "",
	stateOutputs: "",
});

const errors = ref<Record<string, string>>({});
const isSaving = ref(false);

function validateForm(): boolean {
	errors.value = {};

	if (!form.value.name.trim()) {
		errors.value.name = "Name is required";
	}
	if (!form.value.description.trim()) {
		errors.value.description = "Description is required";
	}
	if (!form.value.code.trim()) {
		errors.value.code = "Code is required";
	}

	return Object.keys(errors.value).length === 0;
}

async function handleSave() {
	if (!validateForm()) {
		return;
	}

	isSaving.value = true;
	try {
		const stateInputs = form.value.stateInputs
			.split(",")
			.map((s) => s.trim())
			.filter((s) => s.length > 0);
		const stateOutputs = form.value.stateOutputs
			.split(",")
			.map((s) => s.trim())
			.filter((s) => s.length > 0);

		const response = await fetch("/api/custom-blocks", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				name: form.value.name.trim(),
				description: form.value.description.trim(),
				code: form.value.code,
				state_inputs: stateInputs,
				state_outputs: stateOutputs,
			}),
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || "Failed to create custom block");
		}

		const blockName = form.value.name.trim();

		// Reset form and close modal
		resetForm();
		isOpen.value = false;

		pushToast({
			type: "success",
			message: `Block "${blockName}" created successfully`,
		});

		// Reinitialize session to pick up the new block (similar to file save)
		try {
			await wf.init();
		} catch (error) {
			pushToast({
				type: "error",
				message: "Block created but failed to reload. Please refresh the page.",
			});
		}
	} catch (error) {
		pushToast({
			type: "error",
			message: `Error creating custom block: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isSaving.value = false;
	}
}

function handleClose() {
	if (!isSaving.value) {
		resetForm();
		isOpen.value = false;
	}
}

function resetForm() {
	form.value = {
		name: "",
		description: "",
		code: INIT_CODE,
		stateInputs: "",
		stateOutputs: "",
	};
	errors.value = {};
}

const modalActions = computed<ModalAction[]>(() => [
	{
		desc: "Cancel",
		fn: () => {
			handleClose();
		},
	},
	{
		desc: isSaving.value ? "Saving..." : "Create Block",
		fn: handleSave,
		disabled: isSaving.value,
	},
]);

// Reset form when modal opens
watch(isOpen, async (newValue) => {
	if (newValue) {
		resetForm();
		// Wait for modal and async component to fully render
		await nextTick();
		await nextTick(); // Extra tick for async component
		// Force update the code value after component is ready
		if (form.value.code !== INIT_CODE) {
			form.value.code = INIT_CODE;
		}
	}
});
</script>

<style scoped>
:deep(.WdsModal__main__content) {
	overflow: hidden !important;
	display: flex;
	flex-direction: column;
	height: 100%;
}

:deep(.WdsModal__main) {
	overflow: hidden !important;
	display: flex;
	flex-direction: column;
}

.BuilderSettingsCustomBlock {
	display: grid;
	grid-template-columns: 1fr 1fr;
	grid-template-rows: 1fr;
	gap: 24px;
	padding: 24px;
	min-height: 500px;
	height: 600px;
	max-height: 600px;
	align-items: stretch;
	overflow: hidden;
	flex: 1 1 auto;
}

.BuilderSettingsCustomBlock__left {
	display: flex;
	flex-direction: column;
	gap: 24px;
	min-width: 0;
	overflow-y: auto;
	overflow-x: hidden;
	height: 100%;
}

.BuilderSettingsCustomBlock__right {
	display: flex;
	flex-direction: column;
	min-width: 0;
	height: 100%;
	align-items: stretch;
	overflow: hidden;
}

.BuilderSettingsCustomBlock__codeWrapper {
	display: flex;
	flex-direction: column;
	flex: 1 1 auto;
	min-height: 400px;
	height: 100%;
	overflow: hidden;
}

.BuilderSettingsCustomBlock__codeWrapper :deep(.WdsFieldWrapper__frame) {
	flex: 1 1 auto;
	min-height: 400px;
	display: flex;
	flex-direction: column;
	height: 100%;
	overflow: hidden;
}

.BuilderSettingsCustomBlock__codeEditor {
	flex: 1 1 auto;
	min-height: 400px !important;
	width: 100%;
	height: 100% !important;
	display: flex;
	flex-direction: column;
}

.BuilderSettingsCustomBlock__codeEditor :deep(.BuilderEmbeddedCodeEditor) {
	height: 100% !important;
	min-height: 400px !important;
	flex: 1 1 auto;
	display: flex;
	flex-direction: column;
}

.BuilderSettingsCustomBlock__codeEditor :deep(.BuilderEmbeddedCodeEditor--minimal) {
	min-height: 400px !important;
}

.BuilderSettingsCustomBlock__codeEditor :deep(.editorContainer) {
	flex: 1 1 auto;
	min-height: 400px;
	height: 100% !important;
	width: 100%;
}

.BuilderSettingsCustomBlock__codeEditor :deep(.monaco-editor),
.BuilderSettingsCustomBlock__codeEditor :deep(.monaco-editor .monaco-editor-background),
.BuilderSettingsCustomBlock__codeEditor :deep(.monaco-editor .overflow-guard) {
	height: 100% !important;
	min-height: 400px !important;
}

.BuilderSettingsCustomBlock__textarea {
	width: 100%;
	min-height: 80px;
	padding: 8px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 4px;
	font-size: 14px;
	font-family: inherit;
	resize: vertical;
}

.BuilderSettingsCustomBlock__textarea:focus {
	outline: none;
	border-color: var(--builderPrimaryColor);
}

.BuilderSettingsCustomBlock__textarea--error {
	border-color: var(--builderErrorColor);
}
</style>

