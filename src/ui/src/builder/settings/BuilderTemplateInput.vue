<template>
	<div class="BuilderTemplateInput">
		<template v-if="!props.multiline">
			<WdsTextInput
				ref="input"
				:model-value="props.value"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				:placeholder="props.placeholder"
				:list="props.options ? `list-${props.inputId}` : undefined"
				:invalid="error !== undefined"
				:autofocus="autofocus"
				:readonly="readonly"
				@input="handleInput"
				@blur="closeAutocompletion"
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

		<template v-if="props.multiline">
			<WdsTextareaInput
				ref="input"
				v-capture-tabs
				:variant="props.variant"
				:model-value="props.value"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				rows="3"
				:placeholder="props.placeholder"
				:invalid="error !== undefined"
				:autofocus="autofocus"
				:readonly="readonly"
				@input="handleInput"
			/>
		</template>

		<div
			v-if="autocompleteOptions.length"
			ref="dropdown"
			class="fieldStateAutocomplete"
			tabindex="-1"
			:style="floatingStyles"
		>
			<button
				v-for="(option, optionKey) in autocompleteOptions"
				:key="optionKey"
				class="fieldStateAutocompleteOption"
				:value="optionKey"
				@focusout="closeAutocompletion"
				@focusin="abortClosingAutocompletion"
				@click="() => handleComplete(option.text)"
			>
				<span class="prop">{{ option.text }}</span
				><span class="type">{{ option.type }}</span>
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import Fuse from "fuse.js";
import injectionKeys from "@/injectionKeys";
import {
	PropType,
	computed,
	inject,
	nextTick,
	onUnmounted,
	shallowRef,
	useTemplateRef,
	watch,
} from "vue";
import WdsTextInput from "@/wds/WdsTextInput.vue";
import WdsTextareaInput from "@/wds/WdsTextareaInput.vue";
import { useFloating, size, flip, autoUpdate } from "@floating-ui/vue";

const { secrets } = inject(injectionKeys.secretsManager);

const emit = defineEmits(["input", "update:value"]);

const props = defineProps({
	inputId: { type: String, required: false, default: undefined },
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

const ss = inject(injectionKeys.core);

const input = useTemplateRef("input");
const dropdown = useTemplateRef("dropdown");

const autocompleteOptions = shallowRef<{ text: string; type: string }[]>([]);

const { floatingStyles, update } = useFloating(input, dropdown, {
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

function _get(object: object, path: string[]) {
	return path.reduce((acc, key) => acc?.[key], object);
}

function handleComplete(selectedText: string) {
	let newValue = input.value?.value ?? "";
	const { selectionStart, selectionEnd } = input.value?.getSelection() ?? {};
	const text = newValue.slice(0, selectionStart);
	const full = getPath(text);
	if (full === null) return;
	const keyword = full.at(-1);
	const regexKeyword = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "$"; // escape the keyword to handle properly on a regex
	const replaced = text.replace(
		new RegExp(regexKeyword),
		`${selectedText}${props.type === "template" ? "}" : ""}`,
	);
	const afterText = newValue.slice(selectionEnd).replace(/^(\})+/, ""); // merge the closing bracket to avoid duplicates
	newValue = replaced.concat(afterText);
	emit("input", { target: { value: newValue } });
	emit("update:value", newValue);
	autocompleteOptions.value = [];
	input.value.focus();
	nextTick(() => {
		input.value.setSelectionEnd(replaced.length);
		input.value.setSelectionStart(replaced.length);
	});
}

function typeToString(val: unknown) {
	if (val === null) return "null";
	if (val === undefined) return "undefined";
	return typeof val;
}

function getPath(text: string) {
	if ((props.type ?? "template") === "state") {
		return text.split(".");
	}
	const m = text.match(/@\{([^}{@]*)$/);
	if (!m) {
		return null;
	}
	const raw = m?.[1] ?? "";
	return raw.split(".");
}

/**
 * Escape a key to support the "." and "\" in a state variable
 */
function escapeVariable(key: string) {
	return key.replace(/\\/g, "\\\\").replace(/\./g, "\\.");
}

function handleInput(ev) {
	emit("input", ev);
	emit("update:value", ev.target.value);
	showAutocomplete();
}

const autoCompletionState = computed(() => {
	const userState = ss.userState.value ?? {};
	if (!secrets.value) return userState;

	return {
		...userState,
		vault: secrets.value,
	};
});

function showAutocomplete() {
	const { selectionStart, selectionEnd } = input.value?.getSelection() ?? {};
	const newValue = input.value?.value;
	const collapsed = selectionStart === selectionEnd;
	if (!collapsed) {
		autocompleteOptions.value = [];
		return;
	}
	const text = newValue.slice(0, selectionStart);
	const full = getPath(text);
	if (full === null) {
		autocompleteOptions.value = [];
		return;
	}
	const keyword = full.at(-1);
	const path = full.slice(0, -1);

	const allOptions = Object.entries(
		_get(autoCompletionState.value, path) ?? {},
	).map(([key, val]) => ({
		text: escapeVariable(key),
		type: typeToString(val),
	}));

	const fuse = new Fuse(allOptions, {
		findAllMatches: true,
		includeMatches: true,
		keys: ["text"],
	});

	if (keyword === "") {
		autocompleteOptions.value = allOptions;
		return;
	}
	autocompleteOptions.value = fuse.search(keyword).map((match) => {
		const { item } = match;
		return item;
	});
}

let closeAutocompletionJob: ReturnType<typeof setTimeout> | null;

function closeAutocompletion() {
	// let some time in case user focused on an autocomplete field
	closeAutocompletionJob = setTimeout(() => {
		autocompleteOptions.value = [];
		closeAutocompletionJob = null;
	}, 300);
}

function abortClosingAutocompletion() {
	if (!closeAutocompletionJob) return;
	clearTimeout(closeAutocompletionJob);
	closeAutocompletionJob = null;
}
</script>

<style scoped>
@import "../sharedStyles.css";

.BuilderTemplateInput {
	position: relative;
	width: 100%;
	padding: 0;
}

.fieldStateAutocomplete {
	position: absolute;
	background-color: var(--builderBackgroundColor);
	border: 1px solid var(--builderSeparatorColor);
	border-radius: 4px;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	max-height: 200px;
	overflow-y: auto;
	z-index: 2;
}

.fieldStateAutocompleteOption {
	/* reset button style */
	background-color: inherit;
	border: none;
	width: 100%;
	text-align: left;
	border-radius: 0;

	padding: 8px 12px;
	cursor: pointer;
	display: flex;
	flex-direction: row;
}

.fieldStateAutocompleteOption span.prop {
	flex: 1 1;
	line-height: 24px;
	vertical-align: middle;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.fieldStateAutocompleteOption span.type {
	flex: 0;
	width: fit-content;
	padding: 4px 8px;
	border-radius: 4px;
	background-color: var(--builderSubtleHighlightColor);
}

.fieldStateAutocompleteOption:hover {
	color: inherit;
	background-color: var(--builderSubtleHighlightColorSolid);
}

textarea {
	resize: vertical;
}
</style>
