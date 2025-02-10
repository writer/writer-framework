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
				<BuilderSelect
					:model-value="subMode"
					:options="selectOptions"
					@update:model-value="handleInputSelect"
				/>
			</div>

			<BuilderTemplateInput
				v-if="mode == 'css'"
				ref="freehandInputEl"
				:value="component.content[fieldKey]"
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
	inject,
	nextTick,
	onBeforeUnmount,
	onMounted,
	PropType,
	Ref,
	ref,
	toRefs,
} from "vue";
import { Component } from "@/writerTypes";
import { useComponentActions } from "../useComponentActions";
import injectionKeys from "@/injectionKeys";
import BuilderSelect from "../BuilderSelect.vue";
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

enum SubMode {
	hleft = "start",
	hcenter = "center",
	hright = "end",
	// eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
	vtop = "start",
	// eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
	vcenter = "center",
	// eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
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
		icon: "format_align_left",
	},
	{
		key: SubMode.hcenter,
		label: "Center",
		match: (v) => v == "center",
		default: "center",
		icon: "format_align_center",
	},
	{
		key: SubMode.hright,
		label: "Right",
		match: (v) => v == "end",
		default: "end",
		icon: "format_align_right",
	},
];

const verticalSubmodes: SubModes = [
	{
		key: SubMode.vtop,
		label: "Top",
		match: (v) => v == "start",
		default: "start",
		icon: "vertical_align_top",
	},
	{
		key: SubMode.vcenter,
		label: "Center",
		match: (v) => v == "center",
		default: "center",
		icon: "vertical_align_center",
	},
	{
		key: SubMode.vbottom,
		label: "Bottom",
		match: (v) => v == "end",
		default: "end",
		icon: "vertical_align_bottom",
	},
];

const focusEls: Record<Mode, Ref<HTMLInputElement>> = {
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

const { componentId, fieldKey, direction } = toRefs(props);
const component = computed(() => wf.getComponentById(componentId.value));

const subModes: ComputedRef<SubModes> = computed(() => {
	if (direction.value == "vertical") return verticalSubmodes;
	if (direction.value == "horizontal") return horizontalSubmodes;
	return verticalSubmodes;
});

const selectOptions = computed(() => {
	return subModes.value.map((m) => {
		return { value: m.key, label: m.label, icon: m.icon };
	});
});

const subMode = computed(() => {
	const value = component.value.content[fieldKey.value];
	for (const k in subModes.value) {
		if (value && subModes.value[k].match(value)) {
			return subModes.value[k].key;
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

const getInitialMode = (): Mode => {
	if (!valueCss.value) {
		return "default";
	}

	for (const k in subModes.value) {
		if (subModes.value[k].match(valueCss.value)) {
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
	for (const k in subModes.value) {
		if (subModes.value[k].key == select) {
			const value = subModes.value[k].default;
			component.value.content[fieldKey.value] = value;
			setContentValue(component.value.id, fieldKey.value, value);
		}
	}
};

const handleInputCss = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
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
