<template>
	<span class="BuilderSettingsAPICode" v-if="isWorkflow">
		<BuilderModal
			v-if="isModalVisible"
			:close-action="modalCloseAction"
			icon="code"
			modal-title="API Code"
		>
			<div class="modalContents">
				The following call will create the job and provide you with a
				job ID and a job token.
				<div class="codeContainer">
					<BuilderEmbeddedCodeEditor
						v-model="code"
						class="editor"
						variant="minimal"
						language="shell"
					></BuilderEmbeddedCodeEditor>
				</div>
				Using the job ID and token obtained in the previous call, check
				the status of the job.
				<div class="codeContainer">
					<BuilderEmbeddedCodeEditor
						v-model="codePost"
						class="editor"
						variant="minimal"
						language="shell"
					></BuilderEmbeddedCodeEditor>
				</div>
			</div>
		</BuilderModal>
		<div class="">
			<template v-if="workflowKey">
				<WdsButton variant="tertiary" size="small" @click="showCode">
					<i class="material-symbols-outlined"> code </i> Call via
					API</WdsButton
				>
			</template>
			<template v-else>
				You need to specify a workflow key before this workflow can be
				used in the UI or called via API.
			</template>
		</div>
	</span>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";
import BuilderModal, { ModalAction } from "../BuilderModal.vue";
import BuilderEmbeddedCodeEditor from "../BuilderEmbeddedCodeEditor.vue";
import WdsButton from "@/wds/WdsButton.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const component = computed(() => wf.getComponentById(wfbm.getSelectedId()));

const isWorkflow = computed(
	() => component.value?.type === "workflows_workflow",
);

const workflowKey = computed(() => {
	if (!isWorkflow.value) return;
	return component.value.content?.["key"];
});

const isModalVisible = ref(false);

const code = ref("");
const codePost = ref("");

const modalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		isModalVisible.value = false;
	},
};

function showCode() {
	generateCode();
	isModalVisible.value = true;
}

async function generateCode() {
	const bearerToken = await wf.hashMessage(`create_job_${workflowKey.value}`);
	const baseURL = window.location.origin + window.location.pathname;
	code.value = `
curl --location --request POST '${baseURL}api/job/workflow/${workflowKey.value}' \\
--header 'Content-Type: application/json' \\
--header 'Authorization: Bearer ${bearerToken}' \\
--data '{
    "my_var": 1
}'`.trim();
	codePost.value = `
curl --location '${baseURL}api/job/[JOB_ID]' \\
--header 'Authorization: Bearer [JOB_TOKEN]'`.trim();
}
</script>

<style scoped>
.modalContents {
	display: flex;
	gap: 16px;
	flex-direction: column;
}

.codeContainer {
	height: 100px;
}
</style>
