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
		<template v-if="!isBusy">
			<div class="BlueprintsAutogen__panel">
				<p class="BlueprintsAutogen__error">
					{{ errorMessage }}
				</p>
				<div class="BlueprintsAutogen__buttons">
					<WdsButton variant="tertiary" @click="handleCancel">
						Skip
					</WdsButton>
					<WdsButton variant="secondary" @click="handleAutogen">
						<i class="material-symbols-outlined">bolt</i>
						Autogenerate agent
					</WdsButton>
				</div>
			</div>
		</template>
	</div>
</template>

<script setup lang="ts">
import { inject, onMounted, ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";

import BlueprintsAutogenContents from "./BlueprintsAutogenContents.vue";
import BlueprintsGenerationLoader from "./BlueprintsGenerationLoader.vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "@/builder/useComponentActions";
import injectionKeys from "@/injectionKeys";
import { useWriterTracking } from "@/composables/useWriterTracking";
import { convertAbsolutePathtoFullURL } from "@/utils/url";

type AutogenCreateAction = {
	type: "create";
	components: Component[];
};

export type AutogenLinkActionInfo = {
	id: string;
	newOut: {
		outId: string;
		toNodeId: string;
	};
};

type AutogenLinkAction = {
	type: "link";
	links: AutogenLinkActionInfo[];
};

export type AutogenAction = AutogenCreateAction | AutogenLinkAction;

export type AutogenResult = {
	actions: (AutogenCreateAction | AutogenLinkAction)[];
	messages: string[];
};

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

onMounted(() => {
	tracking.track("blueprints_auto_gen_opened");
});

/**
 * The generation happens with simple ids (aig1, aig2, ...).
 * Component ids are altered to preserve uniqueness across blueprints.
 */
function alterIdForCreate(
	action: AutogenAction & { type: "create" },
	mapping: Record<string, string>,
) {
	action.components.forEach((component) => {
		const newId = generateNewComponentId();
		mapping[component.id] = newId;
		component.id = newId;
	});

	// Switch out ids

	action.components.forEach((component) => {
		component.outs?.forEach((out) => {
			out.toNodeId = mapping[out.toNodeId];
		});
	});

	// Switch results

	action.components.forEach((component) => {
		Object.entries(mapping).forEach(([originalId, newId]) => {
			const regex = new RegExp(
				`(@{\\s*results\\.)aig${originalId}\\b`,
				"g",
			);
			Object.entries(component.content).forEach(([fieldKey, field]) => {
				const newField = field.replace(regex, (_match, capturedAig) =>
					_match.replace(capturedAig, newId),
				);
				component.content[fieldKey] = newField;
			});
		});
	});
}

function alterIdForLink(
	action: AutogenAction & { type: "link" },
	mapping: Record<string, string>,
) {
	action.links.forEach((link) => {
		link.newOut.toNodeId = mapping[link.newOut.toNodeId];
	});
}

function alterIds(actions: AutogenAction[]) {
	const mapping: Record<string, string> = {};

	actions.forEach((action) => {
		if (action.type == "create") {
			alterIdForCreate(action, mapping);
		} else if (action.type == "link") {
			alterIdForLink(action, mapping);
		}
	});

	return actions;
}

async function handleAutogen() {
	const description = prompt.value;
	isBusy.value = true;
	errorMessage.value = null;
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
			},
		);
		if (!response.ok) {
			errorMessage.value = `Agent failed to generate. Try again.`;
			return;
		}

		const data = (await response.json()) as AutogenResult; // Assuming the response is JSON
		const actions: AutogenAction[] = alterIds(data.actions);
		emits("blockGeneration", { actions });
	} catch {
		errorMessage.value = `Agent failed to generate. Try again.`;
		return;
	} finally {
		isBusy.value = false;
	}

	tracking.track("blueprints_auto_gen_completed");
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
