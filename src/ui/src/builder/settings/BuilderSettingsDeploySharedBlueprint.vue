<template>
	<WdsModal
		v-if="isOpen"
		:actions="modalActions"
		:title="deployResult ? 'Blueprint Published' : 'Publish Blueprint'"
		display-close-button
		@close="handleClose"
	>
		<!-- Success view with warnings -->
		<div v-if="deployResult" class="DeploySharedBlueprint">
			<div class="DeploySharedBlueprint__success">
				<WdsIcon
					name="check-circle"
					class="DeploySharedBlueprint__successIcon"
				/>
				<p>
					Blueprint "<strong>{{ deployResult.blueprintName }}</strong
					>" published successfully!
				</p>
			</div>

			<div class="DeploySharedBlueprint__version">
				Version {{ deployResult.version }}
			</div>

			<!-- Warnings -->
			<div
				v-if="deployResult.warnings.length > 0"
				class="DeploySharedBlueprint__notice DeploySharedBlueprint__notice--warning"
			>
				<div class="DeploySharedBlueprint__noticeHeader">
					<WdsIcon name="alert-triangle" />
					<span>Dependencies Detected</span>
				</div>
				<p>
					This shared blueprint has external dependencies. Ensure they
					exist when using this blueprint:
				</p>
				<ul>
					<li v-for="warning in deployResult.warnings" :key="warning">
						{{ warning }}
					</li>
				</ul>
			</div>
		</div>

		<!-- Form view -->
		<div v-else class="DeploySharedBlueprint">
			<!-- Version info -->
			<div v-if="currentVersion" class="DeploySharedBlueprint__versionInfo">
				<WdsIcon name="package" />
				<span
					>Currently published: <strong>v{{ currentVersion }}</strong></span
				>
			</div>
			<div v-else class="DeploySharedBlueprint__versionInfo">
				<WdsIcon name="package" />
				<span>Not yet published</span>
			</div>

			<WdsFieldWrapper label="Name" required>
				<WdsTextInput
					v-model="form.name"
					placeholder="e.g., Data Fetch Pipeline"
					:error="errors.name"
					@update:model-value="handleNameChange"
				/>
			</WdsFieldWrapper>

			<WdsFieldWrapper label="Description" required>
				<textarea
					v-model="form.description"
					placeholder="Describe what this shared blueprint does"
					class="DeploySharedBlueprint__textarea"
					:class="{
						'DeploySharedBlueprint__textarea--error': errors.description,
					}"
				/>
			</WdsFieldWrapper>
		</div>
	</WdsModal>
</template>

<script setup lang="ts">
import { ref, computed, watch, inject } from "vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import injectionKeys from "@/injectionKeys";
import { useToasts } from "@/builder/useToast";
import { useComponentActions } from "@/builder/useComponentActions";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { pushToast } = useToasts();
const { setContentValue } = useComponentActions(wf, wfbm);

interface DeployResult {
	blueprintName: string;
	version: number;
	warnings: string[];
}

const props = defineProps<{
	modelValue: boolean;
	blueprintId: string;
}>();

const emit = defineEmits<{
	"update:modelValue": [value: boolean];
}>();

const isOpen = computed({
	get: () => props.modelValue,
	set: (value) => emit("update:modelValue", value),
});

// Get blueprint component
const blueprint = computed(() => wf.getComponentById(props.blueprintId));

// Get current deployed version from blueprint content
const currentVersion = computed(
	() => blueprint.value?.content?.deployedVersion || null,
);

// Get blueprint name (key) for initial form value
const blueprintName = computed(
	() => blueprint.value?.content?.key || "Shared Blueprint",
);

// Get description if previously deployed
const blueprintDescription = computed(
	() => blueprint.value?.content?.deployedDescription || "",
);

const form = ref({
	name: "",
	description: "",
});

const errors = ref<Record<string, string>>({});
const isDeploying = ref(false);
const deployResult = ref<DeployResult | null>(null);

function validateForm(): boolean {
	errors.value = {};

	if (!form.value.name.trim()) {
		errors.value.name = "Name is required";
	}
	if (!form.value.description.trim()) {
		errors.value.description = "Description is required";
	}

	return Object.keys(errors.value).length === 0;
}

// Sync name changes back to blueprint key
function handleNameChange(newName: string) {
	if (props.blueprintId && newName.trim()) {
		setContentValue(props.blueprintId, "key", newName.trim());
	}
}

async function handleDeploy() {
	if (!validateForm()) {
		return;
	}

	isDeploying.value = true;
	try {
		const response = await fetch("/api/shared-blueprints/deploy", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				blueprint_id: props.blueprintId,
				name: form.value.name.trim(),
				description: form.value.description.trim(),
			}),
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.detail || "Failed to publish blueprint");
		}

		const data = await response.json();

		// Update blueprint's published snippet ID, version, and description
		setContentValue(props.blueprintId, "publishedSnippetId", data.snippet_id);
		setContentValue(props.blueprintId, "deployedVersion", data.version);
		setContentValue(
			props.blueprintId,
			"deployedDescription",
			form.value.description.trim(),
		);

		// Store result to show warnings
		deployResult.value = {
			blueprintName: form.value.name.trim(),
			version: data.version,
			warnings: data.warnings || [],
		};

		// Reinitialize session to pick up the new/updated shared blueprint
		try {
			await wf.init();
		} catch (error) {
			pushToast({
				type: "error",
				message:
					"Blueprint published but failed to reload. Please refresh the page.",
			});
		}
	} catch (error) {
		pushToast({
			type: "error",
			message: `Error publishing blueprint: ${error instanceof Error ? error.message : String(error)}`,
		});
	} finally {
		isDeploying.value = false;
	}
}

function handleClose() {
	if (!isDeploying.value) {
		resetForm();
		isOpen.value = false;
	}
}

function handleDone() {
	resetForm();
	isOpen.value = false;
}

function resetForm() {
	form.value = {
		name: blueprintName.value,
		description: blueprintDescription.value,
	};
	errors.value = {};
	deployResult.value = null;
}

const modalActions = computed<ModalAction[]>(() => {
	if (deployResult.value) {
		return [
			{
				desc: "Done",
				fn: handleDone,
			},
		];
	}
	return [
		{
			desc: "Cancel",
			fn: () => {
				handleClose();
			},
		},
		{
			desc: isDeploying.value ? "Publishing..." : "Publish",
			fn: handleDeploy,
			disabled: isDeploying.value,
		},
	];
});

// Initialize form when modal opens
watch(isOpen, (newValue) => {
	if (newValue) {
		resetForm();
	}
});
</script>

<style scoped>
.DeploySharedBlueprint {
	display: flex;
	flex-direction: column;
	gap: 16px;
	padding: 16px;
}

.DeploySharedBlueprint__versionInfo {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 12px;
	background: var(--builderSubtleBackgroundColor, #f8fafc);
	border-radius: 8px;
	font-size: 13px;
	color: var(--builderSecondaryTextColor);
}

.DeploySharedBlueprint__success {
	display: flex;
	align-items: center;
	gap: 12px;
	padding: 16px;
	background: var(--builderSuccessBackgroundColor, #ecfdf5);
	border-radius: 8px;
	color: var(--builderSuccessColor, #059669);
}

.DeploySharedBlueprint__successIcon {
	font-size: 24px;
	flex-shrink: 0;
}

.DeploySharedBlueprint__success p {
	margin: 0;
}

.DeploySharedBlueprint__version {
	text-align: center;
	font-size: 14px;
	font-weight: 600;
	color: var(--builderPrimaryColor);
}

.DeploySharedBlueprint__notice {
	padding: 12px;
	border-radius: 8px;
	font-size: 13px;
}

.DeploySharedBlueprint__notice--info {
	background: var(--builderInfoBackgroundColor, #eff6ff);
	border: 1px solid var(--builderInfoBorderColor, #bfdbfe);
}

.DeploySharedBlueprint__notice--warning {
	background: var(--builderWarningBackgroundColor, #fffbeb);
	border: 1px solid var(--builderWarningBorderColor, #fcd34d);
}

.DeploySharedBlueprint__noticeHeader {
	display: flex;
	align-items: center;
	gap: 8px;
	font-weight: 600;
	margin-bottom: 8px;
}

.DeploySharedBlueprint__notice p {
	margin: 0 0 8px 0;
	color: var(--builderSecondaryTextColor);
}

.DeploySharedBlueprint__notice ul {
	margin: 0;
	padding-left: 20px;
}

.DeploySharedBlueprint__notice li {
	margin: 4px 0;
}

.DeploySharedBlueprint__textarea {
	width: 100%;
	min-height: 100px;
	padding: 8px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 4px;
	font-size: 14px;
	font-family: inherit;
	resize: vertical;
}

.DeploySharedBlueprint__textarea:focus {
	outline: none;
	border-color: var(--builderPrimaryColor);
}

.DeploySharedBlueprint__textarea--error {
	border-color: var(--builderErrorColor);
}
</style>

