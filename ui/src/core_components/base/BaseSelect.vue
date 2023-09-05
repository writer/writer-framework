<template>
	<div
		class="BaseSelect"
		ref="rootEl"
		v-on:keydown="handleKeydown"
		v-on:focus="handleFocus"
		v-on:blur="handleBlur"
		tabindex="0"
		:class="{
			single: mode == 'single',
			multiple: mode == 'multiple',
		}"
	>
		<div class="selectedOptions">
			<div class="option" v-for="optionKey in selectedOptions">
				<div class="desc">
					{{ options?.[optionKey] }}
				</div>
				<div
					class="remove"
					v-on:click="removeItem(optionKey)"
				>
					<i class="ri-close-line"></i>
				</div>
			</div>
			<input
				type="text"
				v-model="activeText"
				v-on:keydown="handleInputKeydown"
				ref="inputEl"
			/>
		</div>
		<div class="list">
			<div
				class="option"
				:data-list-offset="offset"
				v-for="(option, optionKey, offset) in listOptions"
				v-on:mousemove="highlightItem(offset)"
				v-on:click="selectOption(optionKey)"
				:class="{ highlighted: highlightedOffset == offset }"
			>
				{{ option }}
			</div>
			<div class="empty" v-if="Object.keys(listOptions).length == 0">
				<template v-if="isMaximumCountReached"
					>Only {{ maximumCount }} option{{
						maximumCount > 1 ? "s" : ""
					}}
					allowed.</template
				>
				<template v-else>No results</template>
			</div>
		</div>
		<!-- <select
			:value="formValue"
			v-on:input="($event) => handleInput(($event.target as HTMLInputElement).value, 'ss-option-change')"
		>
			<option
				v-for="(option, optionKey) in fields.options.value"
				:key="optionKey"
				:value="optionKey"
			>
				{{ option }}
			</option>
		</select> -->
	</div>
</template>

<script setup lang="ts">
import { computed, Ref, toRefs } from "vue";
import { ref } from "vue";
import { watch } from "vue";

const props = defineProps<{
	options: Record<string, string>;
	maximumCount: number;
	mode: "single" | "multiple";
}>();

const { options, maximumCount, mode } = toRefs(props);

const rootEl: Ref<HTMLElement | null> = ref(null);
const inputEl: Ref<HTMLElement | null> = ref(null);
const activeText: Ref<string> = ref("");
const highlightedOffset: Ref<number | null> = ref(null);
const selectedOptions: Ref<string[]> = ref([]);

const listOptions = computed(() => {
	if (mode.value == "multiple" && isMaximumCountReached.value) return {};
	const listed = {};
	Object.entries(options.value).forEach(([optionKey, option]) => {
		if (
			mode.value == "multiple" &&
			selectedOptions.value.includes(optionKey)
		)
			return;
		if (
			!option
				.toLocaleLowerCase()
				.includes(activeText.value.toLocaleLowerCase())
		)
			return;
		listed[optionKey] = option;
	});
	return listed;
});

const isMaximumCountReached = computed(() => {
	if (maximumCount.value <= 0) return false;
	if (selectedOptions.value.length < maximumCount.value) return false;
	return true;
});

watch(listOptions, () => {
	enforceHighlightBoundaries();
});

function enforceHighlightBoundaries() {
	if (highlightedOffset.value <= 0) {
		highlightedOffset.value = 0;
		return;
	}
	const maxOffset = Object.keys(listOptions.value).length - 1;
	if (highlightedOffset.value >= maxOffset) {
		highlightedOffset.value = maxOffset;
	}
}

watch(highlightedOffset, () => {
	if (highlightedOffset.value === null) return;
	const el = rootEl.value?.querySelector(
		`[data-list-offset="${highlightedOffset.value}"]`,
	);
	if (!el) return;
	el.scrollIntoView({ block: "nearest", inline: "nearest" });
});

function removeItem(optionKey: string) {
	const index = selectedOptions.value.indexOf(optionKey);
	if (index == -1) return;
	selectedOptions.value.splice(index, 1);
	highlightedOffset.value = null;
}

function blurSelf() {
	const el: HTMLElement = document.activeElement as HTMLElement;
	el.blur();
}

function handleKeydown(ev: KeyboardEvent) {
	const key = ev.key;
	if (key == "Escape") {
		blurSelf();
		return;
	}
	if (key == "Enter") {
		if (highlightedOffset.value === null) return;
		const listKeys = Object.keys(listOptions.value);
		if (!listKeys || listKeys.length == 0) return;
		selectOption(listKeys[highlightedOffset.value]);
		return;
	}
	if (key == "ArrowUp") {
		ev.preventDefault();
		if (highlightedOffset.value === null) {
			const maxOffset = Object.keys(listOptions.value).length - 1;
			highlightedOffset.value = maxOffset;
			return;
		}
		highlightedOffset.value--;
		enforceHighlightBoundaries();
		return;
	}
	if (key == "ArrowDown") {
		ev.preventDefault();
		if (highlightedOffset.value === null) {
			highlightedOffset.value = 0;
			return;
		}
		highlightedOffset.value++;
		enforceHighlightBoundaries();
		return;
	}
}

function handleInputKeydown(ev: KeyboardEvent) {
	if (ev.key == "Backspace" && !activeText.value) {
		selectedOptions.value.pop();
	}
}

function selectOption(optionKey: string) {
	if (mode.value == "single") {
		selectedOptions.value = [];
	} else {
		if (selectedOptions.value.includes(optionKey)) return;
	}
	selectedOptions.value.push(optionKey);
	activeText.value = "";
	if (selectedOptions.value.length == maximumCount.value) {
		blurSelf();
	}
}

function handleBlur(ev: Event) {
	const targetEl = ev.target as HTMLElement;
	if (rootEl.value.contains(targetEl)) return;
	activeText.value = "";
}

function handleFocus() {
	inputEl.value?.focus();
}

function highlightItem(offset: number) {
	highlightedOffset.value = offset;
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.BaseSelect {
	width: fit-content;
	max-width: 100%;
	width: 100%;
	position: relative;
}

label {
	color: var(--primaryTextColor);
}
.selectContainer {
	margin-top: 8px;
}

.selectedOptions {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	padding: 8px;
	border: 1px solid var(--separatorColor);
	width: 100%;
	outline: none;
	min-height: 36px;
}

.selectedOptions .option {
	background: var(--accentColor);
	color: white;
	border-radius: 4px;
	display: flex;
	gap: 4px;
	user-select: none;
	align-items: center;
	outline: none;
}

.selectedOptions .option:focus {
	border: 1px solid var(--primaryTextColor);
}

.selectedOptions .option .desc {
	padding: 8px;
}

.selectedOptions .option .remove {
	padding: 8px;
	backdrop-filter: brightness(95%);
	cursor: pointer;
}

.single .selectedOptions .option .remove {
	display: none;
}

.selectedOptions input {
	min-width: 120px;
	flex: 1 1 auto;
	border: none;
	border-bottom: 1px solid var(--separatorColor);
	transition: 0.2s ease-in-out border;
	display: none;
}

.list {
	display: none;
	margin-top: -1px;
	position: absolute;
	z-index: 10;
	background: var(--containerBackgroundColor);
	width: 100%;
	box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.2);
	border: 1px solid var(--primaryTextColor);
	border-top: none;
	max-height: max(8rem, 20vh);
	overflow-y: auto;
	overflow-x: hidden;
}

.list .option {
	padding: 8px;
	overflow: hidden;
	white-space: nowrap;
	text-overflow: ellipsis;
}

.list .option.highlighted {
	background: rgba(210, 234, 244, 0.8);
	padding: 8px;
}

.list .empty {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 4rem;
	padding-bottom: 8px;
	color: var(--secondaryTextColor);
}

.BaseSelect:focus-within .selectedOptions {
	border: 1px solid var(--primaryTextColor);
	border-bottom: none;
	margin-bottom: 1px;
}

.BaseSelect:focus-within .list {
	display: block;
}

.BaseSelect.single:focus-within .selectedOptions .option {
	display: none;
}

.BaseSelect:focus-within .selectedOptions input {
	display: block;
}
</style>
