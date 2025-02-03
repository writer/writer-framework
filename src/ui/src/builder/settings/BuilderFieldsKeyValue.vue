<template>
	<div
		ref="rootEl"
		class="BuilderFieldsOptions"
		tabindex="-1"
		:data-automation-key="props.fieldKey"
	>
		<WdsTabs
			class="BuilderFieldsOptions__tabs"
			:tabs="tabs"
			:model-value="mode"
			@update:model-value="setMode"
		/>

		<template v-if="mode == 'assisted'">
			<div class="staticList">
				<div
					v-for="(entryValue, entryKey) in assistedEntries"
					:key="entryKey"
					class="entry"
				>
					<div>{{ entryKey }} &middot; {{ entryValue }}</div>
					<button
						variant="subtle"
						@click="removeAssistedEntry(entryKey)"
					>
						<i class="material-symbols-outlined">delete</i>
					</button>
				</div>
			</div>
			<div class="formAdd">
				<BuilderTemplateInput
					ref="assistedKeyEl"
					class="inputKey"
					placeholder="Type a key..."
					:value="formAdd.key"
					@update:value="($event) => (formAdd.key = $event)"
					@keydown.enter="addAssistedEntry"
				/>
				<BuilderTemplateInput
					class="inputValue"
					placeholder="Type a value..."
					:value="formAdd.value"
					@update:value="($event) => (formAdd.value = $event)"
					@keydown.enter="addAssistedEntry"
				/>
				<button @click="addAssistedEntry">
					<i class="material-symbols-outlined">add</i>Add
				</button>
			</div>
		</template>

		<template v-if="mode == 'freehand'">
			<BuilderFieldsObject
				:component-id="component.id"
				:field-key="fieldKey"
			></BuilderFieldsObject>
		</template>
	</div>
</template>

<script setup lang="ts">
import {
	PropType,
	Ref,
	computed,
	inject,
	nextTick,
	onMounted,
	ref,
	toRefs,
	watch,
} from "vue";
import injectionKeys from "@/injectionKeys";
import { useEvaluator } from "@/renderer/useEvaluator";
import type { InstancePath } from "@/writerTypes";
import BuilderFieldsObject from "./BuilderFieldsObject.vue";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import { useComponentActions } from "../useComponentActions";
import WdsTabs, { WdsTabOptions } from "@/wds/WdsTabs.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const props = defineProps({
	componentId: { type: String, required: true },
	fieldKey: { type: String, required: true },
	instancePath: { type: Array as PropType<InstancePath>, required: true },
});

const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const rootEl: Ref<HTMLElement> = ref(null);
const assistedKeyEl: Ref<HTMLInputElement> = ref(null);
type Mode = "assisted" | "freehand";
const mode: Ref<Mode> = ref(null);
const assistedEntries: Ref<Record<string, string | number | null>> = ref({});
const formAdd: Ref<{ key: string; value: string }> = ref({
	key: "",
	value: "",
});

const tabs: WdsTabOptions<Mode>[] = [
	{ label: "Static List", value: "assisted" },
	{ label: "JSON", value: "freehand" },
];

const { getEvaluatedFields } = useEvaluator(wf);

const evaluatedValue = computed<Record<string, string | number | null>>(
	() => getEvaluatedFields(props.instancePath)[fieldKey.value].value,
);

const setMode = async (newMode: Mode) => {
	if (mode.value == newMode) return;
	mode.value = newMode;

	if (mode.value == "assisted") {
		handleSwitchToAssisted();
	}

	await nextTick();
};

const handleSwitchToAssisted = () => {
	assistedEntries.value = evaluatedValue.value ?? {};
};

const addAssistedEntry = () => {
	const { key, value } = formAdd.value;
	if (key === "" || value === "") return;
	assistedEntries.value = { ...assistedEntries.value, [key]: value };
	setContentValue(
		component.value.id,
		fieldKey.value,
		JSON.stringify(assistedEntries.value, null, 2),
	);
	formAdd.value = { key: "", value: "" };
	assistedKeyEl.value.focus();
};

const removeAssistedEntry = (key: string) => {
	const assistedEntriesCopy = assistedEntries.value;
	delete assistedEntriesCopy[key];
	assistedEntries.value = assistedEntriesCopy;

	if (Object.keys(assistedEntries.value).length == 0) {
		setContentValue(component.value.id, fieldKey.value, undefined);
		return;
	}

	setContentValue(
		component.value.id,
		fieldKey.value,
		JSON.stringify(assistedEntries.value, null, 2),
	);
};

/**
 * Watcher for external mutations (like undo/redo).
 */
watch(
	() => component.value?.content[fieldKey.value],
	async () => {
		if (!component.value || !evaluatedValue.value) return;
		assistedEntries.value = evaluatedValue.value;
	},
);

onMounted(async () => {
	// Attempt assisted mode first, if the JSON can be parsed into an object
	if (evaluatedValue.value) {
		assistedEntries.value = evaluatedValue.value;
		setMode("assisted");
	} else {
		setMode("freehand");
	}
});
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderFieldsOptions__tabs {
	margin-bottom: 8px;
}

.staticList {
	padding: 8.5px 12px 8.5px 12px;
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 8px;
}

.staticList:empty::before {
	content: "No entries yet.";
}

.staticList .entry {
	display: flex;
	align-items: center;
	gap: 8px;
	width: 100%;
	max-width: 100%;
}

.staticList .entry div {
	overflow: hidden;
	padding-top: 4px;
	padding-bottom: 4px;
	flex: 1 1 auto;
}

.staticList .entry button {
	flex: 0 0 auto;
}

.formAdd {
	margin-top: 8px;
}

.BuilderTemplateInput {
	margin-bottom: 8px;
}
</style>
