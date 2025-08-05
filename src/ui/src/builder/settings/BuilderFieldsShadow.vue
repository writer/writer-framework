<template>
	<div
		ref="rootEl"
		class="BuilderFieldsShadow"
		tabindex="-1"
		:data-automation-key="props.fieldKey"
	>
		<WdsTabs
			:tabs="tabs"
			:model-value="mode"
			@update:model-value="setMode"
		/>
		<div v-if="mode == 'pick' || mode == 'css'" class="main">
			<div v-if="mode == 'pick'" class="pickerContainer">
				<div class="param">
					<div class="header">
						<div class="name">Offset X</div>
						<div v-show="parsedValue?.offsetX" class="value">
							{{ parsedValue?.offsetX }}px
						</div>
					</div>
					<input
						ref="paramOffsetXEl"
						type="range"
						min="0"
						max="32"
						:value="parsedValue?.offsetX"
						@input="handleInput"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Offset Y</div>
						<div v-show="parsedValue?.offsetY" class="value">
							{{ parsedValue?.offsetY }}px
						</div>
					</div>
					<input
						ref="paramOffsetYEl"
						type="range"
						min="0"
						max="32"
						:value="parsedValue?.offsetY"
						@input="handleInput"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Blur radius</div>
						<div v-show="parsedValue?.blurRadius" class="value">
							{{ parsedValue?.blurRadius }}px
						</div>
					</div>
					<input
						ref="paramBlurRadiusEl"
						type="range"
						min="0"
						max="32"
						:value="parsedValue?.blurRadius"
						@input="handleInput"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Spread radius</div>
						<div v-show="parsedValue?.spreadRadius" class="value">
							{{ parsedValue?.spreadRadius }}px
						</div>
					</div>
					<input
						ref="paramSpreadRadiusEl"
						type="range"
						min="-16"
						max="32"
						:value="parsedValue?.spreadRadius"
						@input="handleInput"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Color</div>
					</div>
					<input
						ref="paramColorEl"
						type="color"
						:value="parsedValue?.color"
						@input="handleInput"
					/>
				</div>
			</div>

			<BuilderTemplateInput
				v-if="mode == 'css'"
				ref="freehandInputEl"
				:value="fieldViewModel"
				:error="error"
				@input="handleCSSInput"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	nextTick,
	onBeforeUnmount,
	onMounted,
	PropType,
	Ref,
	ref,
	toRef,
	useTemplateRef,
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
const freehandInputEl = useTemplateRef("freehandInputEl");
const paramOffsetXEl = useTemplateRef("paramOffsetXEl");
const paramOffsetYEl = useTemplateRef("paramOffsetYEl");
const paramBlurRadiusEl = useTemplateRef("paramBlurRadiusEl");
const paramSpreadRadiusEl = useTemplateRef("paramSpreadRadiusEl");
const paramColorEl = useTemplateRef("paramColorEl");

const focusEls = {
	pick: paramOffsetXEl,
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

const boxShadowRegex =
	/^(?<offsetX>[0-9]+)px (?<offsetY>[0-9]+)px (?<blurRadius>[0-9]+)px (?<spreadRadius>[0-9-]+)px (?<color>#[A-Fa-f0-9]{6})$/;

const getInitialMode = (): Mode => {
	const value = fieldViewModel.value;

	if (!value) return "default";
	const bIsHex = boxShadowRegex.test(value);
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

const handleInput = () => {
	const offsetX = paramOffsetXEl.value.value;
	const offsetY = paramOffsetYEl.value.value;
	const blurRadius = paramBlurRadiusEl.value.value;
	const spreadRadius = paramSpreadRadiusEl.value.value;
	const color = paramColorEl.value.value;
	const boxShadowCSS = `${offsetX}px ${offsetY}px ${blurRadius}px ${spreadRadius}px ${color}`;
	fieldViewModel.value = boxShadowCSS;
};

const handleCSSInput = (ev: Event) => {
	fieldViewModel.value = (ev.target as HTMLInputElement).value;
};

const parsedValue = computed(() => {
	return fieldViewModel.value.match(boxShadowRegex).groups;
});

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
	gap: 4px;
	flex-direction: column;
}

.param > .header {
	display: flex;
	margin-bottom: 4px;
}

.param > .header > .name {
	flex: 1 0 auto;
}

.param > .header > .value {
	margin-left: auto;
}
.param input[type="range"] {
	width: 100%;
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
