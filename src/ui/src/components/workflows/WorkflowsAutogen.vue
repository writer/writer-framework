<template>
	<div class="WorkflowsAutogen">
		<template v-if="!isBusy">
			<div class="main">
				<WdsTextareaInput
					v-model="prompt"
					rows="8"
					placeholder="Describe the blocks you'd like to generate..."
				></WdsTextareaInput>
			</div>
			<div class="buttons">
				<WdsButton @click="handleAutogen">
					<i class="material-symbols-outlined">bolt</i> Generate
				</WdsButton>
				<WdsButton variant="tertiary" @click="handleCancel">
					Cancel
				</WdsButton>
			</div>
		</template>

		<template v-else>
			<WorkflowsLifeLoading></WorkflowsLifeLoading>
			<h2>Generating...</h2>
		</template>
	</div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import WorkflowsLifeLoading from "./WorkflowsLifeLoading.vue";
import { Component } from "@/writerTypes";

const isBusy = ref(false);
const prompt = ref("");

const emits = defineEmits(["blockGeneration"]);

function handleCancel() {
	emits("blockGeneration", null);
}

async function handleAutogen() {
	const description = prompt.value;
	isBusy.value = true;
	const response = await fetch("/api/autogen", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: "Bearer YOUR_ACCESS_TOKEN", // Remove if not needed
		},
		body: JSON.stringify({ description }),
	});

	isBusy.value = false;

	if (!response.ok) {
		throw new Error(`Error: ${response.status} - ${response.statusText}`);
	}

	const data = await response.json(); // Assuming the response is JSON

	const components: Component[] = data.components;
	emits("blockGeneration", { components });
}
</script>

<style scoped>
.WorkflowsAutogen {
	display: flex;
	gap: 24px;
	flex-direction: column;
	align-items: center;
}

.main {
	width: 100%;
}

h2 {
	margin: 0;
	font-size: 24px;
	font-style: normal;
	font-weight: 500;
	line-height: 160%;
}

.buttons {
	display: flex;
	gap: 16px;
}
</style>
