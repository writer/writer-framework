<template>
	<div v-if="isBlueprint" class="BuilderSettingsAPICode">
		<WdsModal
			v-if="isModalVisible"
			title="API Code"
			display-close-button
			:hint="
				isHashAvailable
					? 'Note: For API calls to work, the --enable-jobs-api flag must be active.'
					: undefined
			"
			@close="isModalVisible = false"
		>
			<div class="modalContents">
				<template v-if="isHashAvailable">
					<p>
						The following call will create the job and provide you
						with a job ID and a job token.
					</p>
					<div class="codeContainer">
						<BuilderEmbeddedCodeEditor
							v-model="code"
							class="editor"
							variant="minimal"
							language="shell"
						></BuilderEmbeddedCodeEditor>
					</div>
					<p>
						Using the job ID and token obtained in the previous
						call, check the status of the job. You can use the code
						below, after replacing JOB_ID and JOB_TOKEN for the
						right values.
					</p>
					<div class="codeContainer">
						<BuilderEmbeddedCodeEditor
							v-model="codePost"
							class="editor"
							variant="minimal"
							language="shell"
						></BuilderEmbeddedCodeEditor>
					</div>
				</template>
				<p v-else>
					API code cannot be generated. Please make sure the
					environment variable WRITER_SECRET_KEY has been set up.
				</p>
			</div>
		</WdsModal>
		<template v-if="blueprintKey">
			<WdsButton variant="tertiary" size="small" @click="showCode">
				<i class="material-symbols-outlined"> code </i> Call via
				API</WdsButton
			>
		</template>
		<template v-else>
			<WdsButton
				:disabled="true"
				variant="tertiary"
				size="small"
				data-writer-tooltip="You need to specify a blueprint key before this blueprint can be
				used in the UI or called via API."
			>
				<i class="material-symbols-outlined"> code </i> Call via
				API</WdsButton
			>
		</template>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, ref } from "vue";
import injectionKeys from "@/injectionKeys";
import WdsModal from "@/wds/WdsModal.vue";
import BuilderEmbeddedCodeEditor from "../BuilderEmbeddedCodeEditor.vue";
import WdsButton from "@/wds/WdsButton.vue";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const component = computed(() =>
	wf.getComponentById(wfbm.firstSelectedId.value),
);

const isBlueprint = computed(
	() => component.value?.type === "blueprints_blueprint",
);

const blueprintKey = computed(() => {
	if (!isBlueprint.value) return;
	return component.value.content?.["key"];
});

const isModalVisible = ref(false);

const code = ref("");
const codePost = ref("");
const isHashAvailable = ref(false);

function showCode() {
	generateCode();
	isModalVisible.value = true;
}

async function generateCode() {
	const bearerToken = await wf.hashMessage(
		`create_job_${blueprintKey.value}`,
	);
	isHashAvailable.value = Boolean(bearerToken);
	if (!isHashAvailable.value) return;

	const baseURL = window.location.origin + window.location.pathname;
	code.value = `
curl --location --request POST '${baseURL}api/job/blueprint/${blueprintKey.value}' \\
--header 'Content-Type: application/json' \\
--header 'Authorization: Bearer ${bearerToken}' \\
--data '{
    "my_var": 1
}'`.trim();
	codePost.value = `
curl --location '${baseURL}api/job/JOB_ID' \\
--header 'Authorization: Bearer JOB_TOKEN'`.trim();
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
