<template>
	<div
		ref="rootEl"
		class="BuilderFieldsPadding"
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
				<BuilderSelect
					:model-value="subMode"
					:options="selectOptions"
					@update:model-value="handleInputSelect"
				/>
				<div class="BuilderFieldsPadding__options">
					<template v-if="subMode == SubMode.all_sides">
						<i>All</i>
						<WdsTextInput
							ref="fixedEl"
							type="number"
							:model-value="valuePadding[0]"
							@update:model-value="handleInputs($event, subMode)"
						/>
						<div>px</div>
					</template>
					<template v-if="subMode == SubMode.xy_sides">
						<i>X</i>
						<WdsTextInput
							type="number"
							:model-value="valuePadding[0]"
							@update:model-value="
								handleInputs($event, subMode, 'x')
							"
						/>
						<div>px</div>
						<i>Y</i>
						<WdsTextInput
							type="number"
							:model-value="valuePadding[2]"
							@update:model-value="
								handleInputs($event, subMode, 'y')
							"
						/>
						<div>px</div>
					</template>
					<template v-if="subMode == SubMode.per_side">
						<i>Left</i>
						<WdsTextInput
							type="number"
							:model-value="valuePadding[0]"
							@update:model-value="
								handleInputs($event, subMode, 'left')
							"
						/>
						<div>px</div>
						<i>Right</i>
						<WdsTextInput
							type="number"
							:model-value="valuePadding[1]"
							@update:model-value="
								handleInputs($event, subMode, 'right')
							"
						/>
						<div>px</div>
						<i>Top</i>
						<WdsTextInput
							type="number"
							:model-value="valuePadding[2]"
							@update:model-value="
								handleInputs($event, subMode, 'top')
							"
						/>
						<div>px</div>
						<i>Bottom</i>
						<WdsTextInput
							type="number"
							:model-value="valuePadding[3]"
							@update:model-value="
								handleInputs($event, subMode, 'bottom')
							"
						/>
						<div>px</div>
					</template>
				</div>
			</div>

			<BuilderTemplateInput
				v-if="mode == 'css'"
				ref="freehandInputEl"
				:value="component.content[fieldKey]"
				@input="handleInputCss"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	ComponentInstance,
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
import injectionKeys from "@/injectionKeys";
import BuilderSelect from "../BuilderSelect.vue";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
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
const fixedEl = ref<ComponentInstance<typeof WdsTextInput>>(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

enum SubMode {
	all_sides = "all_sides",
	xy_sides = "XY sides",
	per_side = "Per side",
}

const subModes: Array<{
	key: SubMode;
	label: string;
	match: (v: string) => boolean;
	default: () => string;
	icon?: string;
}> = [
	{
		key: SubMode.all_sides,
		label: "All sides",
		match: (v) => v.split(" ").length == 1 && v.endsWith("px"),
		default: () => (rawPadding.value ? rawPadding.value[0] : "0px"),
	},
	{
		key: SubMode.xy_sides,
		label: "XY sides",
		match: (v) => v.split(" ").length == 2 && v.endsWith("px"),
		default: () =>
			rawPadding.value
				? rawPadding.value[2] + " " + rawPadding.value[0]
				: "0px 0px",
	},
	{
		key: SubMode.per_side,
		label: "Per side",
		match: (v) => v.split(" ").length == 4 && v.endsWith("px"),
		default: () =>
			rawPadding.value
				? [
						rawPadding.value[3],
						rawPadding.value[1],
						rawPadding.value[2],
						rawPadding.value[0],
					].join(" ")
				: "0px 0px 0px 0px",
	},
];

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

const selectOptions = computed(() => {
	return subModes.map((m) => {
		return { value: m.key, label: m.label, icon: "padding" };
	});
});

const subMode = computed(() => {
	const value = component.value.content[fieldKey.value];
	for (const k in subModes) {
		if (value && subModes[k].match(value)) {
			return subModes[k].key;
		}
	}

	return null;
});

const valueCss = computed(() => {
	const value = component.value.content[fieldKey.value];
	if (!value) {
		return "";
	} else {
		return value;
	}
});

const valuePadding = computed(() => {
	const values = rawPadding.value;
	if (!values) {
		return ["0", "0", "0", "0"];
	} else {
		return [
			values[0].substring(0, values[0].length - 2),
			values[1].substring(0, values[1].length - 2),
			values[2].substring(0, values[2].length - 2),
			values[3].substring(0, values[3].length - 2),
		];
	}
});

/**
 * Returns the padding value as an array of 4 values, or null if the value is not valid
 */
const rawPadding = computed(() => {
	const value = component.value.content[fieldKey.value];
	if (!value) {
		return null;
	} else {
		const values = value.split(" ");
		if (values.length == 1 && values[0].endsWith("px")) {
			return [values[0], values[0], values[0], values[0]];
		} else if (
			values.length == 2 &&
			values[0].endsWith("px") &&
			values[0].endsWith("px")
		) {
			return [values[1], values[1], values[0], values[0]];
		} else if (
			values.length == 4 &&
			values[0].endsWith("px") &&
			values[1].endsWith("px") &&
			values[2].endsWith("px") &&
			values[3].endsWith("px")
		) {
			return [values[3], values[1], values[0], values[2]];
		}
	}

	return null;
});

const getInitialMode = (): Mode => {
	if (!valueCss.value) {
		return "default";
	}

	for (const k in subModes) {
		if (subModes[k].match(valueCss.value)) {
			return "pick";
		}
	}

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

const handleInputSelect = (select: string) => {
	for (const k in subModes) {
		if (subModes[k].key == select) {
			const value = subModes[k].default();
			component.value.content[fieldKey.value] = value;
			setContentValue(component.value.id, fieldKey.value, value);
		}
	}

	nextTick(() => {
		fixedEl.value?.focus();
	});
};

const handleInputCss = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};

const handleInputs = (ev: string, subMode: SubMode, inputType?: string) => {
	const value = Number(ev);
	const cssValue = component.value.content[fieldKey.value];

	if (subMode == SubMode.all_sides) {
		setContentValue(component.value.id, fieldKey.value, value + "px");
	} else if (subMode == SubMode.xy_sides) {
		const partCssValues = cssValue.split(" ");
		if (inputType == "x") {
			partCssValues[1] = value + "px";
		} else if (inputType == "y") {
			partCssValues[0] = value + "px";
		}

		setContentValue(
			component.value.id,
			fieldKey.value,
			partCssValues.join(" "),
		);
	} else if (subMode == SubMode.per_side) {
		const partCssValues = cssValue.split(" ");
		if (inputType == "top") {
			partCssValues[0] = value + "px";
		} else if (inputType == "right") {
			partCssValues[1] = value + "px";
		} else if (inputType == "bottom") {
			partCssValues[2] = value + "px";
		} else if (inputType == "left") {
			partCssValues[3] = value + "px";
		}

		setContentValue(
			component.value.id,
			fieldKey.value,
			partCssValues.join(" "),
		);
	}
};

onMounted(() => {
	rootEl.value.addEventListener("focus", autofocus);
});

onBeforeUnmount(() => {
	rootEl.value.removeEventListener("focus", autofocus);
});
</script>

<style scoped>
@import "../sharedStyles.css";
@import "../ico.css";

.main {
	margin-top: 4px;
}

.BuilderFieldsPadding__options {
	margin-top: 8px;
	display: grid;
	grid-template-columns: auto minmax(0, 100%) auto;
	gap: 8px;
	align-items: baseline;
	width: 100%;
}
.BuilderFieldsPadding__options input {
	text-align: right;
}
</style>
