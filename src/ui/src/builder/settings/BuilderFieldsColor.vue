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
					:value="component.content[fieldKey]"
					@input="handleInput"
				/>
			</div>

			<BuilderTemplateInput
				v-if="mode == 'css'"
				ref="freehandInputEl"
				:value="component.content[fieldKey]"
				@input="handleInput"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	inject,
	nextTick,
	onBeforeUnmount,
	onMounted,
	Ref,
	ref,
	toRefs,
} from "vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "../../injectionKeys";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsTabs from "@/wds/WdsTabs.vue";
import {
	BuilderFieldCssMode as Mode,
	BUILDER_FIELD_CSS_TAB_OPTIONS as tabs,
} from "./constants/builderFieldsCssTabs";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const rootEl: Ref<HTMLElement> = ref(null);
const pickerEl: Ref<HTMLInputElement> = ref(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

const focusEls: Record<Mode, Ref<HTMLInputElement>> = {
	pick: pickerEl,
	css: freehandInputEl,
	default: null,
};

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const getInitialMode = (): Mode => {
	const value = component.value.content[fieldKey.value];
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
		setContentValue(component.value.id, fieldKey.value, undefined);
	}
};

const handleInput = (ev: Event) =>
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);

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
