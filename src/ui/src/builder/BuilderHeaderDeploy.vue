<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";
import { computed, ref, watch } from "vue";
import WdsFieldWrapper from "@/wds/WdsFieldWrapper.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";

const cancelModalAction: ModalAction = {
	desc: "Cancel",
	fn: cancelDeploy,
};

const confirmModalActions: ModalAction[] = [
	cancelModalAction,
	{ desc: "Yes, deploy changes", fn: deploy },
];

const apiKeyModalActions = computed<ModalAction[]>(() => [
	cancelModalAction,
	{ desc: "Deploy", fn: deploy, disabled: !hasApiKey.value },
]);

const confirmModalOpen = ref(false);
const apiKeyModalOpen = ref(false);
// fake status
const isDeploying = ref(false);
const isDirty = ref(false);
const apiKey = ref("");
const hasApiKey = computed(() => Boolean(apiKey.value));
const lastDeployedAt = ref<Date | undefined>();

const disabled = computed(() => !isDirty.value || isDeploying.value);

function closeModals() {
	confirmModalOpen.value = false;
	apiKeyModalOpen.value = false;
}

function prepareDeploy() {
	closeModals();

	if (hasApiKey.value) {
		confirmModalOpen.value = true;
	} else {
		apiKeyModalOpen.value = true;
	}
}

function cancelDeploy() {
	closeModals();
}

watch(
	isDirty,
	() => {
		if (!isDirty.value) setTimeout(() => (isDirty.value = true), 2_000);
	},
	{ immediate: true },
);

function deploy() {
	closeModals();
	isDeploying.value = true;
	setTimeout(() => {
		lastDeployedAt.value = new Date();
		isDeploying.value = false;
		isDirty.value = false;
	}, 3_000);
}
</script>

<template>
	<WdsButton
		size="small"
		:disabled="disabled"
		:loading="isDeploying"
		@click="prepareDeploy"
	>
		<template v-if="lastDeployedAt">Deploy changes</template>
		<template v-else>Deploy</template>
		<WdsModal
			v-if="confirmModalOpen"
			title="Are you sure you want to deploy these changes?"
			description="This will replace the current live version of this agent everywhere it is currently deployed."
			size="normal"
			:actions="confirmModalActions"
		/>
		<!-- API key modal -->
		<WdsModal
			v-if="apiKeyModalOpen"
			title="Deploy app"
			description="Add your API Key to deploy this agent"
			size="normal"
			:actions="apiKeyModalActions"
		>
			<WdsFieldWrapper label="API Key">
				<WdsTextInput v-model="apiKey" />
			</WdsFieldWrapper>
		</WdsModal>
	</WdsButton>
</template>

<style scoped>
.BuilderHeaderDeploy__btn {
	min-width: 10ch;
}
</style>
