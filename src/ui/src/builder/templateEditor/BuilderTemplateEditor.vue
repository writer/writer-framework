<script lang="ts" setup>
import injectionKeys from "@/injectionKeys";
import { computed, inject, nextTick, onMounted, useTemplateRef } from "vue";
import { useDynamicUserState } from "../useDynamicUserState";
import { WdsColor } from "@/wds/tokens";
import { extractObjectPaths } from "@/utils/object";
import SharedContentEditable from "@/components/shared/SharedContentEditable.vue";
import BuilderTemplateEditorContent from "./BuilderTemplateEditorContent.vue";
import { useDebouncer } from "@/composables/useDebouncer";
import { useHistoryStack } from "@/composables/useHistoryStack";

defineProps({
	multiline: { type: Boolean, required: false },
});

defineExpose({
	focus,
	getSelection,
	setSelectionEnd,
	setSelectionStart,
});

const wf = inject(injectionKeys.core);
const secretsManager = inject(injectionKeys.secretsManager);

const input = useTemplateRef("input");
const model = defineModel({ type: String });

const { bindings, blueprintsResults, blueprintsSetStates } =
	useDynamicUserState(wf);

type HistoryItem = { content: string; selection: number };
const history = useHistoryStack<HistoryItem>();
const appendUndoStack = useDebouncer(history.push, 500);

const backgroundTagColors = computed(() => {
	return {
		[WdsColor.Green2]: new Set(
			extractObjectPaths(wf.userStateInitial.value),
		),
		[WdsColor.Gray2]: new Set(extractObjectPaths(bindings.value)),
		[WdsColor.Blue2]: new Set([
			...extractObjectPaths(blueprintsSetStates.value),
			...extractObjectPaths(blueprintsResults.value),
		]),
		[WdsColor.Yellow2]: new Set(
			[...extractObjectPaths(secretsManager.secrets.value)].map(
				(v) => `vault.${v}`,
			),
		),
	};
});

function handleInput(value: string) {
	model.value = value;
	appendUndoStack({
		content: model.value,
		selection: input.value?.getSelection() ?? -1,
	});
}

async function applyHistoryItem(value: HistoryItem) {
	model.value = value.content;
	if (value.selection < 0) return;
	await nextTick();
	input.value?.setSelection(value.selection);
}

async function undoChange(e: KeyboardEvent) {
	e.preventDefault();
	const value = history.undo();
	if (value !== undefined) applyHistoryItem(value);
}

async function redoChange(e: KeyboardEvent) {
	e.preventDefault();
	const value = history.redo();
	if (value !== undefined) applyHistoryItem(value);
}

function setSelectionStart(value: number) {
	input.value?.setSelection(value);
}
function setSelectionEnd(value: number) {
	input.value?.setSelection(value);
}

function getSelection() {
	return input.value?.getSelection();
}

function focus() {
	input.value?.focus();
}

onMounted(() => {
	history.push({ content: model.value, selection: -1 });
});
</script>

<template>
	<SharedContentEditable
		ref="input"
		:multiline
		@input="handleInput"
		@keydown.ctrl.z.exact="undoChange"
		@keydown.meta.z.exact="undoChange"
		@keydown.ctrl.y.exact="redoChange"
		@keydown.meta.shift.z.exact="redoChange"
	>
		<BuilderTemplateEditorContent
			:content="model"
			:background-colors="backgroundTagColors"
		/>
	</SharedContentEditable>
</template>
