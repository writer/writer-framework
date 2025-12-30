<template>
	<div
		ref="rootEl"
		class="BuilderFieldsAlign"
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
				<WdsSelect
					ref="pickerEl"
					:model-value="subMode"
					:options="selectOptions"
					@update:model-value="handleInputSelect"
				/>
			</div>

			<BuilderTemplateInput
				v-if="mode == 'css'"
				ref="freehandInputEl"
				:value="fieldViewModel"
				:error="error"
				@input="handleInputCss"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	ComputedRef,
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
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const WdsSelect = defineAsyncComponentWithLoader({
	loader: () => import("@/wds/WdsSelect.vue"),
});

const rootEl = useTemplateRef("rootEl");
const pickerEl = useTemplateRef("pickerEl");
const freehandInputEl = useTemplateRef("freehandInputEl");

enum SubMode {
	hleft = "start",
	hcenter = "center",
	hright = "end",

	vtop = "start",

	vcenter = "center",

	vbottom = "end",
}

type SubModes = {
	key: SubMode;
	label: string;
	match: (v: string) => boolean;
	default: string;
	icon?: string;
}[];

const horizontalSubmodes: SubModes = [
	{
		key: SubMode.hleft,
		label: "Left",
		match: (v) => v == "start",
		default: "start",
		icon: "align-left",
	},
	{
		key: SubMode.hcenter,
		label: "Center",
		match: (v) => v == "center",
		default: "center",
		icon: "align-center",
	},
	{
		key: SubMode.hright,
		label: "Right",
		match: (v) => v == "end",
		default: "end",
		icon: "align-right",
	},
];

const verticalSubmodes: SubModes = [
	{
		key: SubMode.vtop,
		label: "Top",
		match: (v) => v == "start",
		default: "start",
		icon: "arrow-up-to-line",
	},
	{
		key: SubMode.vcenter,
		label: "Center",
		match: (v) => v == "center",
		default: "center",
		icon: "fold-vertical",
	},
	{
		key: SubMode.vbottom,
		label: "Bottom",
		match: (v) => v == "end",
		default: "end",
		icon: "arrow-down-to-line",
	},
];

const focusEls = {
	pick: pickerEl,
	css: freehandInputEl,
	default: null,
};

const props = defineProps({
	componentId: { type: String as PropType<Component["id"]>, required: true },
	fieldKey: { type: String, required: true },
	direction: {
		type: String as PropType<"horizontal" | "vertical">,
		required: true,
	},
	error: { type: String, required: false, default: undefined },
});

const fieldViewModel = useComponentFieldViewModel({
	componentId: toRef(props, "componentId"),
	fieldKey: toRef(props, "fieldKey"),
});

const subModes: ComputedRef<SubModes> = computed(() => {
	if (props.direction == "vertical") return verticalSubmodes;
	if (props.direction == "horizontal") return horizontalSubmodes;
	return verticalSubmodes;
});

const selectOptions = computed(() => {
	return subModes.value.map((m) => {
		return { value: m.key, label: m.label, icon: m.icon };
	});
});

const subMode = computed(() => {
	const value = fieldViewModel.value;

	for (const k in subModes.value) {
		if (value && subModes.value[k].match(value)) {
			return subModes.value[k].key;
		}
	}

	return null;
});

const getInitialMode = (): Mode => {
	if (!fieldViewModel.value) {
		return "default";
	}

	for (const k in subModes.value) {
		if (subModes.value[k].match(fieldViewModel.value)) {
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
		fieldViewModel.value = "";
	}
};

const handleInputSelect = (select: string) => {
	for (const k in subModes.value) {
		if (subModes.value[k].key == select) {
			fieldViewModel.value = subModes.value[k].default;
		}
	}
};

const handleInputCss = (ev: Event) => {
	fieldViewModel.value = (ev.target as HTMLInputElement).value;
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

.main {
	margin-top: 4px;
}
</style>
