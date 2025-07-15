<script lang="ts" setup>
import injectionKeys from "@/injectionKeys";
import { computed, inject, useTemplateRef } from "vue";
import { useDynamicUserState } from "../useDynamicUserState";
import { WdsColor } from "@/wds/tokens";
import { extractObjectPaths } from "@/utils/object";
import SharedContentEditable from "@/components/shared/SharedContentEditable.vue";
import BuilderTemplateEditorContent from "./BuilderTemplateEditorContent.vue";

defineProps({
	multiline: { type: Boolean, required: false },
});

const input = useTemplateRef("input");

defineExpose({
	focus,
	getSelection,
	setSelectionEnd,
	setSelectionStart,
});

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

const wf = inject(injectionKeys.core);
const secretsManager = inject(injectionKeys.secretsManager);

const { bindings, blueprintsResults, blueprintsSetStates } =
	useDynamicUserState(wf);

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

const model = defineModel({ type: String });
</script>

<template>
	<SharedContentEditable ref="input" :multiline @input="model = $event">
		<BuilderTemplateEditorContent
			:content="model"
			:background-colors="backgroundTagColors"
		/>
	</SharedContentEditable>
</template>
