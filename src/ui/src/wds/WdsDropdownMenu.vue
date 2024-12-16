<template>
	<div class="WdsDropdownMenu">
		<div v-if="enableSearch" class="WdsDropdownMenu__search">
			<i class="material-symbols-outlined">search</i>
			<input
				ref="searchInput"
				v-model="searchTerm"
				class="WdsDropdownMenu__search__input"
				type="text"
				placeholder="Search"
				autocomplete="off"
			/>
		</div>
		<button
			v-for="option in optionsFiltered"
			:key="option.value"
			class="WdsDropdownMenu__item"
			:class="{
				'WdsDropdownMenu__item--selected': option.value === selected,
			}"
			@click="$emit('select', option.value)"
		>
			<i v-if="!hideIcons" class="material-symbols-outlined">{{
				getOptionIcon(option)
			}}</i>
			<div class="WdsDropdownMenu__item__label">
				{{ option.label }}
			</div>
			<i
				v-if="option.value === selected"
				class="material-symbols-outlined"
			>
				check
			</i>
		</button>
	</div>
</template>

<script lang="ts">
export type WdsDropdownMenuOption = {
	value: string;
	label: string;
	icon?: string;
};
</script>

<script setup lang="ts">
// from https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/.WDS-Writer-Design-System?node-id=128-396&t=9Gy9MYDycjVV8C2Y-1
import { computed, PropType, ref, watch } from "vue";

const props = defineProps({
	options: {
		type: Array as PropType<WdsDropdownMenuOption[]>,
		default: () => [],
	},
	hideIcons: { type: Boolean, required: false },
	enableSearch: { type: Boolean, required: false },
	selected: { type: String, required: false, default: undefined },
});

const emits = defineEmits({
	select: (value: string) => typeof value === "string",
	search: (value: string) => typeof value === "string",
});

const searchInput = ref<HTMLElement>();
const searchTerm = ref("");

function getOptionIcon(option: WdsDropdownMenuOption) {
	if (props.hideIcons) return "";
	return option.icon ?? "help_center";
}

const optionsFiltered = computed(() => {
	if (!props.enableSearch) return props.options;

	const query = searchTerm.value.toLowerCase();
	return props.options.filter((option) =>
		option.label.toLowerCase().includes(query),
	);
});

watch(searchTerm, () => emits("search", searchTerm.value));
</script>

<style scoped>
.WdsDropdownMenu {
	position: absolute;
	border: 1px solid var(--wdsColorGray2);
	border: none;
	background: #fff;
	z-index: 2;
	width: 100%;
	max-height: 40vh;
	overflow-y: auto;
	border-radius: 8px;

	padding: 8px 10px;

	box-shadow: 0px 1px 8px 0px #bfcbff40;
	box-sizing: border-box;
}
.WdsDropdownMenu:has(.WdsDropdownMenu__search) {
	padding-top: 0px;
}

.WdsDropdownMenu__item {
	background-color: transparent;
	border: none;
	display: block;
	width: 100%;

	display: grid;
	grid-template-columns: auto 1fr auto;
	gap: 8px;
	align-items: center;

	border-radius: 4px;

	padding: 8px;
	font-weight: 400;
	font-size: 0.75rem;
	color: var(--wdsColorGray6);
	cursor: pointer;
	transition: all 0.2s;
	pointer-events: all;
}

.WdsDropdownMenu__item:hover {
	cursor: pointer;
	background-color: var(--wdsColorBlue1);
}

.WdsDropdownMenu__item--selected {
	background-color: var(--wdsColorBlue2);
}
.WdsDropdownMenu__item__label {
	text-overflow: ellipsis;
	overflow: hidden;
	text-align: left;
}

.WdsDropdownMenu__search {
	background-color: var(--wdsColorGray1);
	border-radius: 4px;
	height: 36px;
	width: 100%;

	margin-bottom: 8px;

	display: flex;
	align-items: center;
	justify-content: center;
	gap: 4px;

	padding: 8px;
	padding-top: 16px;
	border: 1px solid transparent;

	color: currentcolor;
}
.WdsDropdownMenu__search:hover {
	border-color: var(--wdsColorBlue1);
}
.WdsDropdownMenu__search:focus-within {
	background-color: white;
	outline: 4px solid var(--wdsColorBlue1);
}

.WdsDropdownMenu__search__input {
	letter-spacing: inherit;
	color: currentcolor;
	padding: 4px 0px 5px;
	border: 0px;
	box-sizing: content-box;
	background: none;
	height: 1.4375em;
	margin: 0px;
	display: block;
	min-width: 0px;
	width: 100%;
	animation-name: mui-auto-fill-cancel;
	animation-duration: 10ms;
	appearance: textfield;
}
.WdsDropdownMenu__search__input:focus-visible {
	outline: none;
}
</style>
