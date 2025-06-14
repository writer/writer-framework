<template>
	<div class="BlueprintsAutogen">
		<template v-if="errorMessage">
			<div class="error-message">
				{{ errorMessage }}
			</div>
			<WdsButton variant="tertiary" @click="handleGoBack">
				Go back
			</WdsButton>
		</template>

		<template v-else-if="!isBusy">
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
			<BlueprintsGenerationLoader></BlueprintsGenerationLoader>
		</template>
	</div>
</template>

<script setup lang="ts">
import { inject, onMounted, ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";

import BlueprintsGenerationLoader from "./BlueprintsGenerationLoader.vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "@/builder/useComponentActions";
import injectionKeys from "@/injectionKeys";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const { generateNewComponentId } = useComponentActions(wf, wfbm);
const tracking = useWriterTracking(wf);

const isBusy = ref(false);
const prompt = ref("");
const errorMessage = ref<string | null>(null); // Track error messages

const emits = defineEmits(["blockGeneration"]);

function handleCancel() {
	emits("blockGeneration", null);
}

function handleGoBack() {
	errorMessage.value = null;
	isBusy.value = false;
}

onMounted(() => {
	tracking.track("blueprints_auto_gen_opened");
});

/**
 * The generation happens with simple ids (aig1, aig2, ...).
 * Component ids are altered to preserve uniqueness across blueprints.
 */
function alterIds(components: Component[]) {
	const mapping: Record<string, string> = {};

	// Switch ids

	components.forEach((c) => {
		const newId = generateNewComponentId();
		mapping[c.id] = newId;
		c.id = newId;
	});

	// Switch out ids

	components.forEach((c) => {
		c.outs?.forEach((out) => {
			out.toNodeId = mapping[out.toNodeId];
		});
	});

	// Switch results

	components.forEach((c) => {
		Object.entries(mapping).forEach(([originalId, newId]) => {
			const regex = new RegExp(
				`(@{\\s*results\\.)aig${originalId}\\b`,
				"g",
			);
			Object.entries(c.content).forEach(([fieldKey, field]) => {
				const newField = field.replace(regex, (_match, capturedAig) =>
					_match.replace(capturedAig, newId),
				);
				c.content[fieldKey] = newField;
			});
		});
	});

	return components;
}

async function handleAutogen() {
	const description = prompt.value;
	isBusy.value = true;
	errorMessage.value = null;
	tracking.track("blueprints_auto_gen_started", { prompt: prompt.value });
	const response = await fetch(convertAbsolutePathtoFullURL("/api/autogen"), {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ description }),
	});

	isBusy.value = false;

	if (!response.ok) {
		errorMessage.value = `Generation failed. Try again`;
		throw new Error(`Error: ${response.status} - ${response.statusText}`);
	}

	const data = await response.json(); // Assuming the response is JSON

	try {
		const components: Component[] = alterIds(data.blueprint?.components);
		emits("blockGeneration", { components });
	} catch (e) {
		errorMessage.value = `Generation failed. Try again`;
		throw e;
	}

	tracking.track("blueprints_auto_gen_completed");
}
</script>

<style scoped>
.BlueprintsAutogen {
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

.error-message {
	color: red;
	font-size: 18px;
	font-weight: 500;
}
</style>
