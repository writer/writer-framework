<template>
	<div class="BuilderTemplateInput">
		<template v-if="!props.multiline">
			<input
				ref="input"
				class="templateInput"
				type="text"
				:value="props.value"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				:placeholder="props.placeholder"
				:list="props.options ? `list-${props.inputId}` : undefined"
				@input="handleInput"
				@blur="handleBlur"
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

		<template v-if="props.multiline">
			<textarea
				ref="input"
				v-capture-tabs
				class="templateInput"
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
				<span class="prop">{{ option.text }}</span
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
	multiline?: boolean;
	type?: "state" | "template";
	options?: Record<string, string>;
	placeholder?: string;
}>();

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
	const full = getPath(text);
	if (full === null) return;
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

const getPath = (text) => {
	if ((props.type ?? "template") === "state") {
		return text.split(".");
	}
	const m = text.match(/@\{([^}{@]*)$/);
	if (!m) {
		return null;
	}
	const raw = m?.[1] ?? "";
	return raw.split(".");
};

const handleInput = (ev) => {
	emit("input", ev);
	emit("update:value", ev.target.value);
	showAutocomplete();
};

const showAutocomplete = () => {
	const { selectionStart, selectionEnd, value: newValue } = input.value ?? {};
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

	const allOptions = Object.entries(_get(ss.getUserState(), path) ?? {}).map(
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

const handleBlur = () => {
	setTimeout(() => {
		autocompleteOptions.value = [];
	}, 10);
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

.fieldStateAutocompleteOption span.prop{
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
