<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";
import { inject, ref } from "vue";
import WdsModal, { ModalAction } from "@/wds/WdsModal.vue";
import {
	useApplicationCloud,
	DeploymentStatus,
} from "@/composables/useApplicationCloud";
import injectionKeys from "@/injectionKeys";
const wf = inject(injectionKeys.core);

const { requestDeployment, deploymentStatus } = useApplicationCloud(wf);

const confirmModalActions: ModalAction[] = [
	{ desc: "Cancel", fn: cancelDeploy },
	{ desc: "Yes, deploy changes", fn: deploy },
];

const confirmModalOpen = ref(false);

function cancelDeploy() {
	confirmModalOpen.value = false;
}

function deploy() {
	confirmModalOpen.value = false;
	requestDeployment();
}
</script>

<template>
	<WdsButton
		size="small"
		:loading="deploymentStatus === DeploymentStatus.InProgress"
		@click="confirmModalOpen = true"
	>
		Deploy
		<WdsModal
			v-if="confirmModalOpen"
			title="Are you sure you want to deploy these changes?"
			description="This will replace the current live version of this agent everywhere it is currently deployed."
			size="normal"
			:actions="confirmModalActions"
		/>
	</WdsButton>
</template>

<style scoped>
.BuilderHeaderDeploy__btn {
	min-width: 10ch;
}
</style>
