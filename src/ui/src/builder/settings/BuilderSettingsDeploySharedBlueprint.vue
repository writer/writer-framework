<template>
	<WdsModal
		v-if="isOpen"
		:actions="modalActions"
		title="Publish Blueprint"
		display-close-button
		@close="handleClose"
	>
		<div class="DeploySharedBlueprint">
			<!-- Version info -->
			<div
				v-if="currentVersion"
				class="DeploySharedBlueprint__versionInfo"
			>
				<WdsIcon name="package" />
				<span
					>Currently published:
					<strong>v{{ currentVersion }}</strong></span
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
						'DeploySharedBlueprint__textarea--error':
							errors.description,
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
import { useWriterTracking } from "@/composables/useWriterTracking";
import { useWriterApi } from "@/composables/useWriterApi";
import { DEFAULT_ORG_ID } from "@/constants/sharedBlueprints";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { pushToast } = useToasts();
const { setContentValue, extractBlueprintComponents } = useComponentActions(
	wf,
	wfbm,
);
const tracking = useWriterTracking(wf);
const { writerApi } = useWriterApi();

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

const blueprint = computed(() => wf.getComponentById(props.blueprintId));

const currentVersion = computed(
	() => blueprint.value?.content?.deployedVersion || null,
);

const blueprintName = computed(
	() => blueprint.value?.content?.key || "Shared Blueprint",
);

const blueprintDescription = computed(
	() => blueprint.value?.content?.deployedDescription || "",
);

const form = ref({
	name: "",
	description: "",
});

const errors = ref<Record<string, string>>({});
const isDeploying = ref(false);

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

	// Use default orgId for local development when writerOrgId is not available
	const orgId = wf.writerOrgId.value || DEFAULT_ORG_ID;

	isDeploying.value = true;
	try {
		// Extract components from frontend
		const components = extractBlueprintComponents(props.blueprintId);

		// Get existing snippet ID if this is an update
		const existingSnippetId =
			blueprint.value?.content?.publishedSnippetId || null;

		const data = await writerApi.publishSharedBlueprint(orgId, {
			title: form.value.name.trim(),
			description: form.value.description.trim(),
			components: components,
			metadata: {},
			existingSnippetId,
		});

		// Update blueprint's published snippet ID, version, and description
		setContentValue(
			props.blueprintId,
			"publishedSnippetId",
			data.snippet_id,
		);
		setContentValue(
			props.blueprintId,
			"deployedVersion",
			String(data.version),
		);
		setContentValue(
			props.blueprintId,
			"deployedDescription",
			form.value.description.trim(),
		);

		pushToast({
			type: "success",
			message: `Blueprint "${form.value.name.trim()}" published (v${data.version})`,
		});
		tracking.track("blueprints_shared_published");

		resetForm();
		isOpen.value = false;

		try {
			await wf.init();
		} catch (_error) {
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

function resetForm() {
	form.value = {
		name: blueprintName.value,
		description: blueprintDescription.value,
	};
	errors.value = {};
}

const modalActions = computed<ModalAction[]>(() => {
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
