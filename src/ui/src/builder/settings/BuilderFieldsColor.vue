<template>
	<div
		ref="rootEl"
		class="BuilderFieldsColor"
		tabindex="-1"
		:data-automation-key="fieldKey"
	>
		<WdsTabs
			:tabs="tabs"
			:model-value="mode"
			@update:model-value="setMode"
		/>
		<div v-if="mode == 'pick' || mode == 'css'" class="main">
			<div v-if="mode == 'pick'" class="pickerContainer">
				<input
					ref="pickerEl"
					type="color"
					:value="fieldViewModel"
					@input="handleInput"
				/>
			</div>

			<BuilderTemplateInput
				v-if="mode == 'css'"
				ref="freehandInputEl"
				:value="fieldViewModel"
				:error="error"
				@input="handleInput"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	nextTick,
	onBeforeUnmount,
	onMounted,
	Ref,
	ref,
	PropType,
	useTemplateRef,
	toRef,
} from "vue";
import { Component } from "@/writerTypes";
import { useComponentFieldViewModel } from "../useComponentFieldViewModel";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsTabs from "@/wds/WdsTabs.vue";
import {
	BuilderFieldCssMode as Mode,
	BUILDER_FIELD_CSS_TAB_OPTIONS as tabs,
} from "./constants/builderFieldsCssTabs";

const rootEl = useTemplateRef("rootEl");
const pickerEl = useTemplateRef("pickerEl");
const freehandInputEl = useTemplateRef("freehandInputEl");

const focusEls = {
	pick: pickerEl,
	css: freehandInputEl,
	default: null,
};

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	error: { type: String, required: false, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

const getInitialMode = (): Mode => {
	const value = fieldViewModel.value;

	if (!value) return "default";
	const hexColorRegex = /#[A-Fa-f0-9]{6}/;
	const bIsHex = hexColorRegex.test(value);
	if (bIsHex) return "pick";
	return "css";
};

const mode: Ref<Mode> = ref(getInitialMode());

const autofocus = () => {
	const focusEl = focusEls[mode.value]?.value;
	if (!focusEl) return;
	focusEl.focus();

	if (typeof focusEl.selectionStart !== "number") return;
	focusEl.selectionStart = focusEl.selectionEnd = focusEl.value.length;
};

const setMode = async (newMode: Mode) => {
	if (mode.value == newMode) return;
	mode.value = newMode;
	await nextTick();
	autofocus();

	if (newMode === "default") {
		fieldViewModel.value = "";
	}
};

const handleInput = (ev: Event) =>
	(fieldViewModel.value = (ev.target as HTMLInputElement).value);

onMounted(() => {
	rootEl.value.addEventListener("focus", autofocus);
});

onBeforeUnmount(() => {
	rootEl.value.removeEventListener("focus", autofocus);
});
</script>

<style scoped>
@import "../sharedStyles.css";

.main {
	margin-top: 4px;
}

.pickerContainer {
	display: flex;
	gap: 8px;
	flex-direction: column;
}

input[type="color"] {
	width: 100%;
	height: 40px;
	min-height: 40px;
	border-radius: 8px;
	border: 1px solid var(--separatorColor);
	display: block;
	background-color: var(--wdsColorWhite);
	color-scheme: light;
	cursor: pointer;
	padding: 2px;
	transition:
		border-color ease-in-out 0.2s,
		box-shadow ease-in-out 0.2s;
	outline: none;
}

input[type="color"]:hover {
	border-color: var(--wdsColorBlue3);
}

input[type="color"]:focus {
	border-color: var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}

input[type="color"]::-webkit-color-swatch-wrapper {
	padding: 0;
	border-radius: 6px;
	overflow: hidden;
}

input[type="color"]::-webkit-color-swatch {
	border: none;
	border-radius: 6px;
}

input[type="color"]::-moz-color-swatch {
	border: none;
	border-radius: 6px;
}
</style>
