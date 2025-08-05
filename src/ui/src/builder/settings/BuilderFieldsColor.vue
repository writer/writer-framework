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
	defaultValue: "",
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
input[type="color"] {
	width: 100%;
	height: 34px;
	border-radius: 8px;
	border: 1px solid var(--separatorColor);

	display: block;
	height: 40px;
}
</style>
