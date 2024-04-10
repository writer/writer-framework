<template>
	<div class="BuilderTemplateInput">
		<template v-if="type === 'input'">
			<input
				ref="input"
				type="text"
				:value="props.value"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				:placeholder="props.placeholder"
				:list="props.options ? `list-${props.inputId}` : undefined"
				@input="handleInput"
			/>
			<datalist v-if="props.options" :id="`list-${props.inputId}`">
				<option
					v-for="(option, optionKey) in options"
					:key="optionKey"
					:value="optionKey"
				>
					<template
						v-if="option.toLowerCase() !== optionKey.toLowerCase()"
					>
						{{ option }}
					</template>
				</option>
			</datalist>
		</template>

		<template v-if="type === 'textarea'">
			<textarea
				ref="input"
				v-capture-tabs
				variant="code"
				:value="props.value"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				:placeholder="props.placeholder"
				@input="handleInput"
			></textarea>
		</template>

		<div v-if="autocompleteOptions.length" class="fieldStateAutocomplete">
			<div
				v-for="(option, optionKey) in autocompleteOptions"
				:key="optionKey"
				class="fieldStateAutocompleteOption"
				:value="optionKey"
				@click="() => handleComplete(option.text)"
			>
				<span class="text">{{ option.text }}</span
				><span class="type">{{ option.type }}</span>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, ref, nextTick } from "vue";
import injectionKeys from "../injectionKeys";
import Fuse from "fuse.js";

const emit = defineEmits(["input", "update:value"]);
const props = defineProps<{
	inputId?: string;
	value?: string;
	type?: "input" | "textarea";
	options?: Record<string, string>;
	placeholder?: string;
}>();
const type = props.type ?? "input";

const ss = inject(injectionKeys.core);
const autocompleteOptions = ref<string[]>([]);
const input = ref<HTMLInputElement | null>(null);

defineExpose({
	focus: () => input.value?.focus(),
});

function _get(object: object, path: string[]) {
	return path.reduce((acc, key) => acc?.[key], object);
}

const handleComplete = (selectedText) => {
	let newValue = input.value?.value ?? "";
	const { selectionStart, selectionEnd } = input.value ?? {};
	const text = newValue.slice(0, selectionStart);
	const m = text.match(/@\{([^}{@]*)$/);
	if (!m) {
		return;
	}
	const full = (m?.[1] ?? "").split(".");
	const keyword = full.at(-1);
	const replaced = text.replace(new RegExp(keyword + "$"), selectedText);
	newValue = replaced + newValue.slice(selectionEnd);
	emit("input", { target: { value: newValue } });
	emit("update:value", newValue);
	autocompleteOptions.value = [];
	input.value.focus();
	nextTick(() => {
		input.value.selectionEnd = replaced.length;
		input.value.selectionStart = replaced.length;
	});
};

const typeToString = (val) => {
	if (val === null) return "null";
	if (val === undefined) return "undefined";
	return typeof val;
};

const handleInput = (ev) => {
	const newValue = ev.target.value;
	emit("input", ev);
	emit("update:value", ev.target.value);
	const { selectionStart, selectionEnd } = input.value ?? {};
	const collapsed = selectionStart === selectionEnd;
	if (!collapsed) {
		autocompleteOptions.value = [];
		return;
	}
	const text = newValue.slice(0, selectionStart);
	const m = text.match(/@\{([^}{@]*)$/);
	if (!m) {
		autocompleteOptions.value = [];
		return;
	}

	const full = (m?.[1] ?? "").split(".");
	const keyword = full.at(-1);
	const path = full.slice(0, -1);

	const allOptions = Object.entries(_get(ss.getUserState(), path)).map(
		([key, val]) => ({
			text: key,
			type: typeToString(val),
		}),
	);

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
};
</script>

<style scoped>
@import "./sharedStyles.css";

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
	width: 100%;
	z-index: 2;
}

.fieldStateAutocompleteOption {
	padding: 8px 12px;
	cursor: pointer;
	display: flex;
	flex-direction: row;
}

.fieldStateAutocompleteOption span.text {
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
	background-color: var(--builderSubtleHighlightColorSolid);
}
</style>
