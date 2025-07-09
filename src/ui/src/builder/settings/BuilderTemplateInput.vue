<template>
	<div ref="root" class="BuilderTemplateInput">
		<BuilderTemplateInputInput
			ref="input"
			:model-value="props.value"
			:placeholder="props.placeholder"
			:list="props.options ? `list-${props.inputId}` : undefined"
			:invalid="error !== undefined"
			:autofocus="autofocus"
			:readonly="readonly"
			:left-icon="type === 'state' ? 'alternate_email' : undefined"
			:right-icon="rightIcon"
			:multiline
			@right-icon-click="
				showAutocompletions = showAutocompletions
					? undefined
					: 'template'
			"
			@input="handleInput"
			@click="onClick"
		/>

		<div
			v-if="showAutocompletions"
			ref="dropdown"
			class="BuilderTemplateInput__dropdown"
			:style="floatingStyles"
		>
			<BuilderStateSelectorDropdown
				v-if="showAutocompletions === 'template'"
				:hide-secrets="type === 'state'"
				:hide-blueprint-results="type === 'state'"
				:allow-create="type === 'state'"
				:query="templateDropdownQuery"
				:component-id="componentId"
				@update:model-value="onSelectTemplateAutocomplete"
			/>
			<WdsDropdownMenu
				v-else-if="staticOptions.length"
				:options="staticOptions"
				@select="onSelectStaticAutocomplete"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	PropType,
	ref,
	useTemplateRef,
	nextTick,
	watch,
	computed,
	onUnmounted,
} from "vue";
import { useFloating, size, flip, autoUpdate } from "@floating-ui/vue";
import BuilderStateSelectorDropdown from "../stateDropdown/BuilderStateSelectorDropdown.vue";
import BuilderTemplateInputInput from "./BuilderTemplateInputInput.vue";
import {
	autocompleteTemplateVariable,
	getCurrentOpenedTemplate,
} from "@/utils/template";
import { useFocusWithin } from "@/composables/useFocusWithin";
import WdsDropdownMenu, {
	WdsDropdownMenuOption,
} from "@/wds/WdsDropdownMenu.vue";

const props = defineProps({
	inputId: { type: String, required: false, default: undefined },
	componentId: { type: String, required: false, default: undefined },
	value: { type: String, required: false, default: undefined },
	multiline: { type: Boolean, required: false },
	variant: {
		type: String as PropType<"code" | "text">,
		required: false,
		default: undefined,
	},
	type: {
		type: String as PropType<"state" | "template">,
		required: false,
		default: "template",
	},
	options: {
		type: Object as PropType<Record<string, string>>,
		required: false,
		default: undefined,
	},
	placeholder: { type: String, required: false, default: undefined },
	error: { type: String, required: false, default: undefined },
	autofocus: { type: Boolean },
	readonly: { type: Boolean },
});

const emit = defineEmits(["input", "update:value"]);

const root = useTemplateRef("root");
const input = useTemplateRef("input");
const dropdown = useTemplateRef("dropdown");

const showAutocompletions = ref<"template" | "static" | undefined>();

const { floatingStyles, update } = useFloating(root, dropdown, {
	placement: "bottom-start",
	middleware: [
		flip(),
		// take the width of the reference element
		size({
			apply({ rects, elements }) {
				Object.assign(elements.floating.style, {
					minWidth: `${rects.reference.width}px`,
					maxWidth: `${rects.reference.width}px`,
				});
			},
		}),
	],
	strategy: "fixed",
});
useFloatingAutoUpdate();

function useFloatingAutoUpdate() {
	let autoUpdateCleanup: ReturnType<typeof autoUpdate> | undefined;

	function cleanup() {
		if (autoUpdateCleanup) autoUpdateCleanup();
		autoUpdateCleanup = undefined;
	}

	watch(dropdown, () => {
		cleanup();
		if (dropdown.value) {
			autoUpdateCleanup = autoUpdate(input, dropdown.value, update);
		}
	});

	onUnmounted(() => cleanup());
}

defineExpose({
	focus: () => input.value?.focus(),
});

const rightIcon = computed(() => {
	if (props.type === "template" || props.multiline) return undefined;

	return showAutocompletions.value
		? "keyboard_arrow_up"
		: "keyboard_arrow_down";
});

const staticOptions = computed<WdsDropdownMenuOption[]>(() => {
	if (!props.options) return [];

	return Object.entries(props.options).reduce<WdsDropdownMenuOption[]>(
		(acc, [k, v]) => {
			if (k.includes(props.value)) {
				acc.push({
					value: k,
					label: v,
				});
			}

			return acc;
		},
		[],
	);
});

function onClick() {
	if (staticOptions.value.length > 0) showAutocompletions.value = "static";
}

const templateDropdownQuery = computed(() => {
	let value = input.value?.value ?? "";
	if (!value) return "";
	const { selectionStart } = input.value?.getSelection() ?? {};

	if (props.type === "template") {
		const before = value.slice(0, selectionStart);
		return getCurrentOpenedTemplate(before);
	} else {
		return value;
	}
});

const hasFocusInRoot = useFocusWithin(root);
watch(hasFocusInRoot, async () => {
	if (!hasFocusInRoot.value) {
		await nextTick();
		setTimeout(() => {
			showAutocompletions.value = undefined;
		}, 300);
	}
});

async function onSelectTemplateAutocomplete(selectedText: string) {
	let newValue = input.value?.value ?? "";
	const { selectionStart, selectionEnd } = input.value?.getSelection() ?? {};
	let newSelectionStart = selectionStart ?? newValue.length;

	if (props.type === "template") {
		const before = newValue.slice(0, selectionStart);
		const after = newValue.slice(selectionEnd).replace(/^(\})+/, ""); // merge the closing bracket to avoid duplicates

		const newBefore = autocompleteTemplateVariable(before, selectedText);

		newValue = `${newBefore}${after}`;
		newSelectionStart = newBefore.length;
	} else {
		newValue = selectedText;
		newSelectionStart = selectedText.length;
	}

	emit("input", { target: { value: newValue } });
	emit("update:value", newValue);

	if (!input.value) return;

	input.value.focus();
	showAutocompletions.value = undefined;

	await nextTick();

	input.value.setSelectionStart(newSelectionStart);
}
async function onSelectStaticAutocomplete(selectedText: string) {
	emit("input", { target: { value: selectedText } });
	emit("update:value", selectedText);

	if (!input.value) return;

	input.value.focus();
	showAutocompletions.value = undefined;

	await nextTick();

	input.value.setSelectionStart(selectedText.length);
}

function handleInput(ev) {
	let newValue = String(ev.target.value ?? "");
	emit("input", ev);
	emit("update:value", newValue);

	if (props.type === "state") {
		showAutocompletions.value = "template";
		return;
	}

	if (staticOptions.value.some((v) => v.value.includes(newValue))) {
		showAutocompletions.value = "static";
		return;
	}

	const { selectionStart } = input.value?.getSelection() ?? {};
	const text = newValue.slice(0, selectionStart);

	const shouldShowAutocomplete =
		!!text.match(/@\{([^}{@]*)$/) ||
		text.endsWith("@") ||
		!!templateDropdownQuery.value;
	showAutocompletions.value = shouldShowAutocomplete ? "template" : undefined;
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderTemplateInput {
	position: relative;
	width: 100%;
	padding: 0;
}

.BuilderTemplateInput__dropdown {
	z-index: 2;
}

textarea {
	resize: vertical;
}
</style>
