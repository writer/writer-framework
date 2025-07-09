<template>
	<WdsTextInputLayout
		:left-icon
		:right-icon
		:invalid
		:variant
		class="BuilderTemplateInputInput"
		:class="{ 'BuilderTemplateInputInput--multiline': multiline }"
		@right-icon-click="$emit('rightIconClick')"
		@click="focus"
	>
		<SharedContentEditable
			ref="input"
			class="BuilderTemplateInputInput__input"
			:multiline
			@input="onChange"
		>
			<StateWithPills
				:content="model"
				:background-colors="backgroundTagColors"
			/>
		</SharedContentEditable>
	</WdsTextInputLayout>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, PropType, useTemplateRef } from "vue";
import StateWithPills from "../stateDropdown/StateWithPills.vue";
import SharedContentEditable from "@/components/shared/SharedContentEditable.vue";
import WdsTextInputLayout from "@/wds/WdsTextInputLayout.vue";
import { useDynamicUserState } from "../useDynamicUserState";
import injectionKeys from "@/injectionKeys";
import { extractObjectPaths } from "@/utils/object";
import { WdsColor } from "@/wds/tokens";

const model = defineModel({ type: String });

const props = defineProps({
	leftIcon: { type: String, required: false, default: undefined },
	rightIcon: { type: String, required: false, default: undefined },
	invalid: { type: Boolean, required: false },
	variant: { type: String as PropType<"ghost">, default: undefined },
	autofocus: { type: Boolean },
	multiline: { type: Boolean, required: false },
});

const emit = defineEmits({
	rightIconClick: () => true,
	input: (event: InputEvent) => !!event,
});

defineExpose({
	focus,
	getSelection,
	value: model,
	setSelectionEnd,
	setSelectionStart,
});

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
		[WdsColor.Blue2]: new Set(
			...extractObjectPaths(blueprintsSetStates.value),
			...extractObjectPaths(blueprintsResults.value),
		),
		[WdsColor.Yellow2]: new Set(
			[...extractObjectPaths(secretsManager.secrets.value)].map(
				(v) => `vault.${v}`,
			),
		),
	};
});

const input = useTemplateRef("input");

onMounted(() => {
	if (props.autofocus) focus();
});

async function onChange(value: string) {
	model.value = value;
	emit("input", {
		target: { value },
	} as unknown as InputEvent);
}

function setSelectionStart(value: number) {
	if (!input.value) return;
	input.value.setSelection(value);
}
function setSelectionEnd(value: number) {
	if (!input.value) return;
	input.value.setSelection(value);
}

function getSelection() {
	const res = { selectionStart: undefined, selectionEnd: undefined };

	if (!input.value) return res;

	const selection = input.value.getSelection();
	res.selectionStart = selection;
	res.selectionEnd = selection;

	return res;
}

function focus() {
	input.value?.focus();
}
</script>

<style scoped>
.BuilderTemplateInputInput__input {
	background: transparent;
	font-size: 14px;
	border: none;
	width: 100%;
	min-height: 21px;
	height: 100%;
}
.BuilderTemplateInputInput__input:focus {
	outline: none;
}
.BuilderTemplateInputInput--multiline .BuilderTemplateInputInput__input {
	min-height: 64px;
}
</style>
