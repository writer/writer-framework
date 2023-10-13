<template>
	<div class="BuilderFieldsHAlign" tabindex="-1" ref="rootEl">
		<div class="chipStackContainer">
			<div class="chipStack">
				<button
					class="chip"
					tabindex="0"
					:class="{ active: mode == 'default' }"
					v-on:click="
						() => {
							setMode('default');
							setContentValue(component.id, fieldKey, 'left');
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
				<BuilderSelect :defaultValue=subMode :options=selectOptions @select="handleInputSelect"/>
			</div>

			<input
				type="text"
				ref="freehandInputEl"
				:value="component.content[fieldKey]"
				v-on:input="handleInputCss"
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
import BuilderSelect from "./BuilderSelect.vue";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const rootEl: Ref<HTMLElement> = ref(null);
const pickerEl: Ref<HTMLInputElement> = ref(null);
const fixedEl: Ref<HTMLInputElement> = ref(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

type Mode = "pick" | "css" | "default";

enum SubMode {
	left = "start",
	center = "center",
	right = "end",
}

const subModes: Array<{key: SubMode, label: string, match: (v: string) => boolean, default: string, icon?: string}> = [
	{'key': SubMode.left, label: 'Left', match: (v) => v == "start", default: 'start', icon: "ri-align-left"},
	{'key': SubMode.center, label: 'Center', match: (v) => v == 'center', default: 'center', icon: "ri-align-center"},
	{'key': SubMode.right, label: 'Right', match: (v) => v == "end", default: 'end', icon: "ri-align-right"},
]


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
const component = computed(() => ss.getComponentById(componentId.value));

const selectOptions = computed(() => {
	return subModes.map((m) => {
		return { value: m.key, label: m.label, icon: m.icon };
	});
});

const subMode = computed(() => {
	const value = component.value.content[fieldKey.value]
	for (const k in subModes) {
		if (value && subModes[k].match(value)) {
			return subModes[k].key
		}
	}

	return null
})

const valueCss = computed(() => {
	const value = component.value.content[fieldKey.value]
	if (!value) {
		return ''
	} else {
		return value
	}
})

const valuePickFixed = computed(() => {
	const value = component.value.content[fieldKey.value]
	if (!value) {
		return null
	} else if (value.endsWith('px')) {
		return value.substring(0, value.length - 2)
	}

	return null
})

const getInitialMode = (): Mode => {
	if (!valueCss.value) {
		return "default";
	}

	for (const k in subModes) {
		if (subModes[k].match(valueCss.value)) {
			return "pick"
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
};

const handleInputSelect = (select: string) => {
	for (const k in subModes) {
		if (subModes[k].key == select) {
			const value = subModes[k].default;
			component.value.content[fieldKey.value] = value;
			setContentValue(
					component.value.id,
					fieldKey.value,
					value
			);
		}
	}
}

const handleInputCss = (ev: Event) => {
	setContentValue(
			component.value.id,
			fieldKey.value,
			(ev.target as HTMLInputElement).value
	)
}

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

.fixedContainer {
	display: flex;
	flex-direction: row;
	gap: 8px;
	padding: 8px;
}
</style>
