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

			<div
				v-if="isGlobalBlueprintProposalsEnabled"
				class="DeploySharedBlueprint__globalOption"
			>
				<label class="DeploySharedBlueprint__checkbox">
					<input v-model="form.proposeAsGlobal" type="checkbox" />
					<span>Propose as global blueprint</span>
				</label>
				<p class="DeploySharedBlueprint__hint">
					Global blueprints are available to all organizations and
					require approval via GitHub PR.
				</p>
			</div>

			<div v-if="prUrl" class="DeploySharedBlueprint__success">
				<p>Pull request created successfully!</p>
				<a :href="prUrl" target="_blank" rel="noopener noreferrer">
					{{ prUrl }}
				</a>
			</div>
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

const isGlobalBlueprintProposalsEnabled = computed(
	() =>
		Array.isArray(wf.featureFlags.value) &&
		wf.featureFlags.value.includes("global_blueprint_proposals"),
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
	proposeAsGlobal: false,
});

const errors = shallowRef<Record<string, string>>({});
const isDeploying = ref(false);
const prUrl = ref<string | null>(null);

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
	prUrl.value = null;

	try {
		// Extract components from frontend
		const components = extractBlueprintComponents(props.blueprintId);

		if (form.value.proposeAsGlobal) {
			// Propose as global blueprint via GitHub PR
			const result = await writerApi.proposeSharedBlueprintGlobal({
				title: form.value.name.trim(),
				description: form.value.description.trim(),
				components: components,
				metadata: {},
			});

			prUrl.value = result.pr_url;

			pushToast({
				type: "success",
				message: `Global blueprint proposed! A PR has been created for review.`,
			});
			tracking.track("blueprints_global_proposed");

			// Don't close the modal - show the PR URL
		} else {
			// Publish to org's shared blueprints
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
		proposeAsGlobal: false,
	};
	errors.value = {};
	prUrl.value = null;
}

const modalActions = computed<ModalAction[]>(() => {
	const publishText = form.value.proposeAsGlobal ? "Propose" : "Publish";
	const publishingText = form.value.proposeAsGlobal
		? "Proposing..."
		: "Publishing...";

	// If PR was created, show close button only
	if (prUrl.value) {
		return [
			{
				desc: "Close",
				fn: handleClose,
			},
		];
	}

	return [
		{
			desc: "Cancel",
			fn: handleClose,
		},
		{
			desc: isDeploying.value ? publishingText : publishText,
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

.DeploySharedBlueprint__globalOption {
	display: flex;
	flex-direction: column;
	gap: 4px;
	padding: 12px;
	background: var(--builderSubtleSeparatorColor);
	border-radius: 4px;
}

.DeploySharedBlueprint__checkbox {
	display: flex;
	align-items: center;
	gap: 8px;
	cursor: pointer;
	font-size: 14px;
}

.DeploySharedBlueprint__checkbox input {
	cursor: pointer;
}

.DeploySharedBlueprint__hint {
	font-size: 12px;
	color: var(--builderSecondaryTextColor);
	margin: 0;
}

.DeploySharedBlueprint__success {
	display: flex;
	flex-direction: column;
	gap: 8px;
	padding: 12px;
	background: var(--builderSuccessBackgroundColor, #e6f7e6);
	border: 1px solid var(--builderSuccessColor, #4caf50);
	border-radius: 4px;
}

.DeploySharedBlueprint__success p {
	margin: 0;
	font-weight: 500;
}

.DeploySharedBlueprint__success a {
	color: var(--builderPrimaryColor);
	word-break: break-all;
}
</style>
