<template>
	<WdsModal
		v-if="isOpen"
		:actions="modalActions"
		title="Publish Blueprint"
		display-close-button
		@close="handleClose"
	>
		<div class="DeploySharedBlueprint">
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
import { ref, computed, watch, inject, shallowRef } from "vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import injectionKeys from "@/injectionKeys";
import { useToasts } from "@/builder/useToast";
import { useComponentActions } from "@/builder/useComponentActions";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { useWriterApi } from "@/composables/useWriterApi";

const props = defineProps<{
	blueprintId: string;
}>();

const isOpen = defineModel({ type: Boolean });

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);
const { pushToast } = useToasts();
const { setContentValue, extractBlueprintComponents } = useComponentActions(
	wf,
	wfbm,
);
const tracking = useWriterTracking(wf);
const { writerApi } = useWriterApi();

const blueprint = computed(() => wf.getComponentById(props.blueprintId));

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

const errors = shallowRef<Record<string, string>>({});
const isDeploying = ref(false);

function validateForm(): boolean {
	const newErrors: Record<string, string> = {};

	if (!form.value.name.trim()) {
		newErrors.name = "Name is required";
	}
	if (!form.value.description.trim()) {
		newErrors.description = "Description is required";
	}

	errors.value = newErrors;
	return Object.keys(newErrors).length === 0;
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

	const orgId = wf.writerOrgId.value;
	if (!orgId) {
		pushToast({
			type: "error",
			message:
				"Organization ID is required. Please set up your environment variable.",
		});
		return;
	}

	isDeploying.value = true;
	try {
		// Extract components from frontend
		const components = extractBlueprintComponents(props.blueprintId);

		const data = await writerApi.publishSharedBlueprint(orgId, {
			title: form.value.name.trim(),
			description: form.value.description.trim(),
			components: components,
			metadata: {},
		});

		// Update blueprint's published snippet ID and description
		setContentValue(
			props.blueprintId,
			"publishedSnippetId",
			data.snippet_id,
		);
		setContentValue(
			props.blueprintId,
			"deployedDescription",
			form.value.description.trim(),
		);

		pushToast({
			type: "success",
			message: `Blueprint "${form.value.name.trim()}" published successfully`,
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
			fn: handleClose,
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
