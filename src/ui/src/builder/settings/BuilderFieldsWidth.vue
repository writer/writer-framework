<template>
	<div
		ref="rootEl"
		class="BuilderFieldsWidth"
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
				<div v-if="subMode == SubMode.fixed" class="fixedContainer">
					<WdsTextInput
						ref="fixedEl"
						type="number"
						:model-value="valuePickFixed"
						@update:model-value="handleInputFixed"
					/>
					<div>px</div>
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
import injectionKeys from "../../injectionKeys";
import BuilderSelect from "../BuilderSelect.vue";
import BuilderTemplateInput from "./BuilderTemplateInput.vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsTabs, { WdsTabOptions } from "@/wds/WdsTabs.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(wf, ssbm);

const rootEl: Ref<HTMLElement> = ref(null);
const pickerEl: Ref<HTMLInputElement> = ref(null);
const fixedEl = ref<ComponentInstance<typeof WdsTextInput>>(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

type Mode = "pick" | "css" | "default";

const tabs: WdsTabOptions<Mode>[] = [
	{
		label: "Default",
		value: "default",
	},
	{
		label: "CSS",
		value: "css",
	},
	{
		label: "Pick",
		value: "pick",
	},
];

enum SubMode {
	fixed = "fixed",
	fit_content = "fit-content",
	full = "full",
}

const subModes: Array<{
	key: SubMode;
	label: string;
	match: (v: string) => boolean;
	default: string;
	icon?: string;
}> = [
	{
		key: SubMode.fixed,
		label: "Fixed",
		match: (v) => v.endsWith("px"),
		default: "160px",
	},
	{
		key: SubMode.fit_content,
		label: "Fit Content",
		match: (v) => v == "fit-content",
		default: "fit-content",
	},
	{
		key: SubMode.full,
		label: "Full",
		match: (v) => v == "100%",
		default: "100%",
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
		return {
			value: m.key,
			label: m.label,
			icon: "width",
		};
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

const valuePickFixed = computed(() => {
	const value = component.value.content[fieldKey.value];
	if (!value) {
		return null;
	} else if (value.endsWith("px")) {
		return value.substring(0, value.length - 2);
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
			const value = subModes[k].default;
			component.value.content[fieldKey.value] = value;
			setContentValue(component.value.id, fieldKey.value, value);
		}
	}

	if (select == SubMode.fixed) {
		nextTick(() => {
			fixedEl.value.focus();
		});
	}
};

const handleInputCss = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};

const handleInputFixed = (ev: string) => {
	setContentValue(component.value.id, fieldKey.value, `${ev}px`);
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

.fixedContainer {
	margin-top: 8px;
	display: flex;
	flex-direction: row;
	align-items: center;
	gap: 8px;
}
</style>
