<template>
	<div class="BuilderFieldsShadow" tabindex="-1" ref="rootEl">
		<div class="chipStackContainer">
			<div class="chipStack">
				<button
					class="chip"
					tabindex="0"
					:class="{ active: mode == 'default' }"
					v-on:click="
						() => {
							setMode('default');
							setContentValue(component.id, fieldKey, undefined);
						}
					"
				>
					Default
				</button>
				<button
					class="chip"
					tabindex="0"
					:class="{ active: mode == 'css' }"
					v-on:click="setMode('css')"
				>
					CSS
				</button>
				<button
					class="chip"
					:class="{ active: mode == 'pick' }"
					tabindex="0"
					v-on:click="setMode('pick')"
				>
					Pick
				</button>
			</div>
		</div>

		<div class="main" v-if="mode == 'pick' || mode == 'css'">
			<div class="pickerContainer" v-if="mode == 'pick'">
				<div class="param">
					<div class="header">
						<div class="name">Offset X</div>
						<div class="value" v-show="parsedValue?.offsetX">
							{{ parsedValue?.offsetX }}px
						</div>
					</div>
					<input
						type="range"
						min="0"
						max="32"
						:value="parsedValue?.offsetX"
						v-on:input="handleInput"
						ref="paramOffsetXEl"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Offset Y</div>
						<div class="value" v-show="parsedValue?.offsetY">
							{{ parsedValue?.offsetY }}px
						</div>
					</div>
					<input
						type="range"
						min="0"
						max="32"
						:value="parsedValue?.offsetY"
						v-on:input="handleInput"
						ref="paramOffsetYEl"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Blur radius</div>
						<div class="value" v-show="parsedValue?.blurRadius">
							{{ parsedValue?.blurRadius }}px
						</div>
					</div>
					<input
						type="range"
						min="0"
						max="32"
						:value="parsedValue?.blurRadius"
						v-on:input="handleInput"
						ref="paramBlurRadiusEl"
					/>
				</div>
				<div class="param">
					<div class="header">
						<div class="name">Spread radius</div>
						<div class="value" v-show="parsedValue?.spreadRadius">
							{{ parsedValue?.spreadRadius }}px
						</div>
					</div>
					<input
						type="range"
						min="-16"
						max="32"
						:value="parsedValue?.spreadRadius"
						v-on:input="handleInput"
						ref="paramSpreadRadiusEl"
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
						v-on:input="handleInput"
					/>
				</div>
			</div>

			<input
				type="text"
				ref="freehandInputEl"
				:value="component.content[fieldKey]"
				v-on:input="handleCSSInput"
				v-if="mode == 'css'"
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
import { Component } from "../streamsyncTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const rootEl: Ref<HTMLElement> = ref(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);
const paramOffsetXEl: Ref<HTMLInputElement> = ref(null);
const paramOffsetYEl: Ref<HTMLInputElement> = ref(null);
const paramBlurRadiusEl: Ref<HTMLInputElement> = ref(null);
const paramSpreadRadiusEl: Ref<HTMLInputElement> = ref(null);
const paramColorEl: Ref<HTMLInputElement> = ref(null);

type Mode = "pick" | "css" | "default";

const focusEls: Record<Mode, Ref<HTMLInputElement>> = {
	pick: paramOffsetXEl,
	css: freehandInputEl,
	default: null,
};

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));

const boxShadowRegex =
	/^(?<offsetX>[0-9]+)px (?<offsetY>[0-9]+)px (?<blurRadius>[0-9]+)px (?<spreadRadius>[0-9\-]+)px (?<color>#[A-Fa-f0-9]{6})$/;

const getInitialMode = (): Mode => {
	const value = component.value.content[fieldKey.value];
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
};

const handleInput = () => {
	const offsetX = paramOffsetXEl.value.value;
	const offsetY = paramOffsetYEl.value.value;
	const blurRadius = paramBlurRadiusEl.value.value;
	const spreadRadius = paramSpreadRadiusEl.value.value;
	const color = paramColorEl.value.value;
	const boxShadowCSS = `${offsetX}px ${offsetY}px ${blurRadius}px ${spreadRadius}px ${color}`;
	setContentValue(component.value.id, fieldKey.value, boxShadowCSS);
};

const handleCSSInput = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value
	);
};

const parsedValue = computed(() => {
	const value = component.value.content[fieldKey.value];
	const match = value?.match(boxShadowRegex)?.groups;
	return match;
});

onMounted(() => {
	rootEl.value.addEventListener("focus", autofocus);
});

onBeforeUnmount(() => {
	rootEl.value.removeEventListener("focus", autofocus);
});
</script>

<style scoped>
@import "./sharedStyles.css";

.chipStackContainer {
	padding: 12px;
	margin-top: 4px;
	padding-bottom: 12px;
}
.main {
	border-top: 1px solid var(--builderSeparatorColor);
	padding: 12px;
}

.pickerContainer {
	display: flex;
	gap: 8px;
	flex-direction: column;
}

.param > .header {
	display: flex;
	margin-bottom: 8px;
}

.param > .header > .name {
	flex: 1 0 auto;
}

.param > .header > .value {
	margin-left: auto;
}
</style>
