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
			@right-icon-click="showAutocompletions = !showAutocompletions"
			@input="handleInput"
		/>
		<template v-if="false && !props.multiline">
			<WdsTextInput
				:model-value="props.value"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				:placeholder="props.placeholder"
				:list="props.options ? `list-${props.inputId}` : undefined"
				:invalid="error !== undefined"
				:autofocus="autofocus"
				:readonly="readonly"
				:left-icon="type === 'state' ? 'alternate_email' : undefined"
				:right-icon="rightIcon"
				@right-icon-click="showAutocompletions = !showAutocompletions"
				@input="handleInput"
			/>
			<datalist v-if="props.options" :id="`list-${props.inputId}`">
				<option
					v-for="(option, optionKey) in options"
					:key="optionKey"
					:value="optionKey"
				>
					<template
						v-if="
							option.toLowerCase() !==
							String(optionKey).toLowerCase()
						"
					>
						{{ option }}
					</template>
				</option>
			</datalist>
		</template>

		<div
			v-if="showAutocompletions"
			ref="dropdown"
			class="BuilderTemplateInput__dropdown"
			:style="floatingStyles"
		>
			<BuilderStateSelectorDropdown
				:hide-secrets="type === 'state'"
				:hide-blueprint-results="type === 'state'"
				:allow-create="type === 'state'"
				:query="dropdownQuery"
				:component-id="componentId"
				@update:model-value="onSelectAutocomplete"
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
import WdsTextInput from "@/wds/WdsTextInput.vue";
import { useFloating, size, flip, autoUpdate } from "@floating-ui/vue";
import BuilderStateSelectorDropdown from "../stateDropdown/BuilderStateSelectorDropdown.vue";
import BuilderTemplateInputInput from "./BuilderTemplateInputInput.vue";
import {
	autocompleteTemplateVariable,
	getCurrentOpenedTemplate,
} from "@/utils/template";
import { useFocusWithin } from "@/composables/useFocusWithin";

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

const showAutocompletions = ref(false);

const { floatingStyles, update } = useFloating(root, dropdown, {
	placement: "bottom-start",
	middleware: [
		flip(),
		// take the width of the reference element
		size({
			apply({ rects, elements }) {
				Object.assign(elements.floating.style, {
					minWidth: `${rects.reference.width}px`,
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

const dropdownQuery = computed(() => {
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
watch(hasFocusInRoot, () => {
	if (!hasFocusInRoot.value) {
		nextTick().then(() => (showAutocompletions.value = false));
	}
});

async function onSelectAutocomplete(selectedText: string) {
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
	showAutocompletions.value = false;

	await nextTick();

	input.value.setSelectionStart(newSelectionStart);
}

function handleInput(ev) {
	let newValue = String(ev.target.value ?? "");
	emit("input", ev);
	emit("update:value", newValue);

	if (props.type === "template") {
		const { selectionStart } = input.value?.getSelection() ?? {};
		const text = newValue.slice(0, selectionStart);

		showAutocompletions.value =
			!!text.match(/@\{([^}{@]*)$/) ||
			text.endsWith("@") ||
			!!dropdownQuery.value;
	} else {
		showAutocompletions.value = true;
	}
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
