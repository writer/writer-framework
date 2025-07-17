<template>
	<div class="BlueprintsAutogen">
		<h2>
			{{
				isBusy
					? "Generating agent"
					: "What would you like this agent to do?"
			}}
		</h2>
		<BlueprintsAutogenContents :is-busy="isBusy" :class="{ busy: isBusy }">
			<template v-if="!isBusy">
				<div
					class="BlueprintsAutogen__main"
					:class="{ error: errorMessage }"
				>
					<WdsTextareaInput
						v-model="prompt"
						rows="10"
						placeholder="Describe the blocks you'd like to generate..."
						style="height: 100%"
					></WdsTextareaInput>
				</div>
			</template>

			<template v-else>
				<BlueprintsGenerationLoader />
			</template>
		</BlueprintsAutogenContents>
		<div class="BlueprintsAutogen__panel">
			<p class="BlueprintsAutogen__error">
				{{ errorMessage }}
			</p>
			<div class="BlueprintsAutogen__buttons">
				<template v-if="isBusy">
					<WdsButton variant="tertiary" @click="handleBack">
						Back
					</WdsButton>
				</template>
				<WdsButton variant="tertiary" @click="handleCancel">
					Skip
				</WdsButton>
				<WdsButton
					variant="secondary"
					:disabled="isBusy"
					@click="handleAutogen"
				>
					<WdsIcon name="sparkles" />
					{{ isBusy ? "Autogenerating..." : "Autogenerate agent" }}
				</WdsButton>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, onMounted, ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";

import BlueprintsAutogenContents from "./BlueprintsAutogenContents.vue";
import BlueprintsGenerationLoader from "./BlueprintsGenerationLoader.vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "@/builder/useComponentActions";
import { useToasts } from "@/builder/useToast";
import injectionKeys from "@/injectionKeys";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

const wf = inject(injectionKeys.core);
const wfbm = inject(injectionKeys.builderManager);

const { generateNewComponentId } = useComponentActions(wf, wfbm);
const tracking = useWriterTracking(wf);

const { pushToast } = useToasts();

const isBusy = ref(false);
const prompt = ref("");
const errorMessage = ref<string | null>(null); // Track error messages
let autogenController: AbortController | null = null;

const emits = defineEmits(["blockGeneration"]);

function handleCancel() {
	if (autogenController) {
		autogenController.abort();
	}
	emits("blockGeneration", null);
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

	if (!description) {
		errorMessage.value =
			"Please add instructions to create your blueprint.";
		return;
	}

	isBusy.value = true;
	errorMessage.value = null;

	if (autogenController) {
		autogenController.abort();
	}

	autogenController = new AbortController();

	tracking.track("blueprints_auto_gen_started", { prompt: prompt.value });

	try {
		const response = await fetch(
			convertAbsolutePathtoFullURL("/api/autogen"),
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ description }),
				signal: autogenController.signal,
			},
		);
		if (!response.ok) {
			errorMessage.value = `Agent failed to generate. Try again.`;
			return;
		}

		const data = await response.json(); // Assuming the response is JSON
		const components: Component[] = alterIds(data.blueprint?.components);
		emits("blockGeneration", { components });
		pushToast({
			type: "success",
			message: `Blueprint generated`,
		});
	} catch (err) {
		if (err.name !== "AbortError") {
			errorMessage.value = `Agent failed to generate. Try again.`;
		}
		return;
	} finally {
		isBusy.value = false;
		autogenController = null;
	}

	tracking.track("blueprints_auto_gen_completed");
}

function handleBack() {
	if (autogenController) {
		autogenController.abort();
	}
	isBusy.value = false;
}
</script>

<style scoped>
.BlueprintsAutogen {
	display: flex;
	gap: 20px;
	flex-direction: column;
}

.BlueprintsAutogen__main {
	width: 100%;
	padding: 0;
	margin: 0;
}

.BlueprintsAutogen__main.error {
	border: 1px solid var(--wdsColorOrange5);
	border-radius: 8px;
	box-sizing: border-box;
}

h2 {
	margin: 0;
	font-size: 24px;
	font-style: normal;
	font-weight: 500;
	line-height: 160%;
	text-align: left;
}

.BlueprintsAutogen__panel {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.BlueprintsAutogen__error {
	display: flex;
	color: var(--wdsColorOrange5);
	font-size: 12px;
	font-weight: 400;
	line-height: 180%;
	align-items: flex-start;
}

.BlueprintsAutogen__buttons {
	display: flex;
	gap: 16px;
	justify-content: flex-end;
	padding-right: 20px;
}
</style>
