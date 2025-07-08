<template>
	<div
		class="BuilderTemplateInputInput"
		:class="{
			'BuilderTemplateInputInput--ghost': variant === 'ghost',
			'BuilderTemplateInputInput--multiline': multiline,
		}"
		:aria-invalid="invalid"
		:style="{
			gridTemplateColumns: gridTemplateColumns,
		}"
		@click="focus"
	>
		<i v-if="leftIcon" class="material-symbols-outlined">{{ leftIcon }}</i>
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
		<button
			v-if="rightIcon"
			class="BuilderTemplateInputInput__rightIcon"
			type="button"
			@click="$emit('rightIconClick')"
		>
			<i class="material-symbols-outlined">{{ rightIcon }}</i>
		</button>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, PropType, useTemplateRef } from "vue";
import StateWithPills from "../stateDropdown/StateWithPills.vue";
import SharedContentEditable from "@/components/shared/SharedContentEditable.vue";
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

const gridTemplateColumns = computed(() =>
	[
		props.leftIcon ? "auto" : undefined,
		"minmax(0, 1fr)",
		props.rightIcon ? "auto" : undefined,
	]
		.filter(Boolean)
		.join(" "),
);

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
.BuilderTemplateInputInput {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 14px;
	outline: none;
	color: var(--primaryTextColor);
	background: transparent;
	transition: box-shadow ease-in-out 0.2s;

	cursor: pointer;
	display: grid;
	align-items: center;
	gap: 8px;
}

.BuilderTemplateInputInput--multiline {
	resize: vertical;
}

.BuilderTemplateInputInput:focus-within {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

.BuilderTemplateInputInput--ghost {
	border-color: transparent;
	background-color: transparent;
	transition:
		box-shadow,
		background-color,
		border-color ease-in-out 0.2s;
}
.BuilderTemplateInputInput--ghost:disabled {
	cursor: not-allowed;
}
.BuilderTemplateInputInput--ghost:not(:disabled):hover {
	background-color: transparent;
	border-color: var(--wdsColorBlue3);
}
.BuilderTemplateInputInput--ghost:not(:disabled):focus,
.BuilderTemplateInputInput--ghost:not(:disabled):focus-within {
	background-color: transparent;
}

.BuilderTemplateInputInput i {
	color: var(--wdsColorGray5);
}

.BuilderTemplateInputInput__rightIcon {
	border: none;
	background-color: transparent;
	display: flex;
	align-items: center;
	cursor: pointer;
}
.BuilderTemplateInputInput__input {
	background: transparent;
	font-size: 14px;
	border: none;
	width: 100%;
	min-height: 21px;
	height: 100%;
}
.BuilderTemplateInputInput--multiline .BuilderTemplateInputInput__input {
	min-height: 64px;
}
.BuilderTemplateInputInput__input:focus {
	border: none;
	box-shadow: none;
	outline: none;
}
.BuilderTemplateInputInput[aria-invalid="true"] {
	border-color: var(--wdsColorOrange5);
}
</style>
