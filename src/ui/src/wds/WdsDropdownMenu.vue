<template>
	<div class="WdsDropdownMenu">
		<div
			v-if="(enableSearch || enableMultiSelection) && !loading"
			class="WdsDropdownMenu__header"
		>
			<div
				v-if="enableMultiSelection"
				class="WdsDropdownMenu__header__multiSelect"
			>
				<div class="WdsDropdownMenu__header__multiSelect__count">
					{{ headerSelectCountText }}
				</div>
				<button
					class="WdsDropdownMenu__header__multiSelect__clear"
					role="button"
					@click="$emit('select', [])"
				>
					Clear all
				</button>
			</div>
			<div v-if="enableSearch" class="WdsDropdownMenu__header__search">
				<i class="material-symbols-outlined">search</i>
				<input
					ref="searchInput"
					v-model="searchTerm"
					class="WdsDropdownMenu__header__search__input"
					type="text"
					placeholder="Search"
					autocomplete="off"
					:disabled="loading"
				/>
			</div>
		</div>

		<template v-if="loading">
			<button
				v-for="index in 6"
				:key="index"
				class="WdsDropdownMenu__item"
			>
				<WdsSkeletonLoader
					v-if="enableMultiSelection || !hideIcons"
					style="width: 20px"
				/>
				<div class="WdsDropdownMenu__item__label">
					<WdsSkeletonLoader />
				</div>
			</button>
		</template>

		<template v-else-if="enableMultiSelection">
			<WdsCheckbox
				v-for="option in optionsFiltered"
				:key="option.value"
				class="WdsDropdownMenu__checkbox"
				:checked="isSelected(option.value)"
				:label="option.label"
				:detail="option.detail"
				:data-automation-key="option.value"
				:disabled="option.disabled"
				:model-value="isSelected(option.value)"
				@update:model-value="onSelect(option.value)"
			/>
		</template>

		<template v-else>
			<button
				v-for="option in optionsFiltered"
				:key="option.value"
				class="WdsDropdownMenu__item"
				:class="{
					'WdsDropdownMenu__item--selected': isSelected(option.value),
					'WdsDropdownMenu__item--hideIcon': hideIcons,
				}"
				:data-automation-key="option.value"
				:disabled="option.disabled"
				@click="onSelect(option.value)"
			>
				<template v-if="!hideIcons">
					<div
						v-if="Array.isArray(option.icon)"
						class="WdsDropdownMenu__item__icon WdsDropdownMenu__item__icon--img"
					>
						<SharedImgWithFallback :urls="option.icon" />
					</div>
					<i
						v-else
						class="material-symbols-outlined WdsDropdownMenu__item__icon"
						>{{ getOptionIcon(option) }}</i
					>
				</template>
				<div
					class="WdsDropdownMenu__item__label"
					:data-writer-tooltip="option.label"
					data-writer-tooltip-strategy="overflow"
				>
					{{ option.label }}
				</div>
				<div
					v-if="option.detail"
					class="WdsDropdownMenu__item__detail"
					:data-writer-tooltip="option.detail"
					data-writer-tooltip-strategy="overflow"
				>
					{{ option.detail }}
				</div>
				<i
					v-if="isSelected(option.value)"
					class="material-symbols-outlined"
				>
					check
				</i>
			</button>
		</template>
	</div>
</template>

<script lang="ts">
export type WdsDropdownMenuOption = {
	value: string;
	label: string;
	detail?: string;
	/**
	 * A font icon or an array of image URL
	 */
	icon?: string | string[];
	disabled?: boolean;
};
</script>

<script setup lang="ts">
// from https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/.WDS-Writer-Design-System?node-id=128-396&t=9Gy9MYDycjVV8C2Y-1
import { computed, PropType, ref, watch } from "vue";
import WdsSkeletonLoader from "./WdsSkeletonLoader.vue";
import WdsCheckbox from "./WdsCheckbox.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";

const props = defineProps({
	options: {
		type: Array as PropType<
			WdsDropdownMenuOption[] | Readonly<WdsDropdownMenuOption[]>
		>,
		default: () => [],
	},
	hideIcons: { type: Boolean, required: false },
	enableSearch: { type: Boolean, required: false },
	enableMultiSelection: { type: Boolean, required: false },
	selected: {
		type: [Array, String] as PropType<string[] | string>,
		required: false,
		default: () => {},
	},
	loading: { type: Boolean, required: false },
});

const emits = defineEmits({
	select: (value: string | string[]) =>
		typeof value === "string" || Array.isArray(value),
	search: (value: string) => typeof value === "string",
});

const searchTerm = ref("");

const headerSelectCountText = computed(() => {
	const selectedArray = Array.isArray(props.selected)
		? props.selected
		: [props.selected];
	const count = selectedArray.filter(Boolean).length;
	return `${count}/${props.options.length} selected`;
});

const optionsFiltered = computed(() => {
	if (!props.enableSearch) return props.options;

	const query = searchTerm.value.toLowerCase();
	return props.options.filter(
		(option) =>
			option.label.toLowerCase().includes(query) ||
			option.detail?.toLowerCase().includes(query),
	);
});

function getOptionIcon(option: WdsDropdownMenuOption) {
	if (props.hideIcons) return "";
	return option.icon ?? "help_center";
}

function isSelected(value: string) {
	return Array.isArray(props.selected)
		? props.selected.includes(value)
		: props.selected === value;
}

const optionsValues = computed(
	() => new Set(props.options.map((o: WdsDropdownMenuOption) => o.value)),
);

function onSelect(value: string) {
	if (!props.enableMultiSelection) return emits("select", value);

	const values = new Set(props.selected);
	values.has(value) ? values.delete(value) : values.add(value);
	emits(
		"select",
		[...values].filter((v) => optionsValues.value.has(v)),
	);
}

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

	box-shadow: var(--wdsShadowMenu);
	box-sizing: border-box;
}
.WdsDropdownMenu:has(.WdsDropdownMenu__header) {
	padding-top: 0px;
}

.WdsDropdownMenu__checkbox,
.WdsDropdownMenu__item {
	min-height: 36px;
}

.WdsDropdownMenu__checkbox {
	margin-top: 8px;
	margin-bottom: 8px;
}

.WdsDropdownMenu__item {
	background-color: transparent;
	border: none;
	display: block;
	width: 100%;

	display: grid;
	grid-template-columns: 1fr auto;
	column-gap: 8px;
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
.WdsDropdownMenu__item:has(.WdsDropdownMenu__item__icon) {
	grid-template-columns: auto 1fr auto;
}
.WdsDropdownMenu__item:has(.WdsDropdownMenu__item__icon)
	.WdsDropdownMenu__item__detail {
	grid-column-start: 2;
}
.WdsDropdownMenu__item__icon {
	grid-row-start: 1;
	grid-row-end: -1;
	display: flex;
	align-items: center;
}

.WdsDropdownMenu__item:hover {
	cursor: pointer;
	background-color: var(--wdsColorBlue1);
}

.WdsDropdownMenu__item--selected {
	background-color: var(--wdsColorBlue2);
}
.WdsDropdownMenu__item--hideIcon {
	grid-template-columns: 1fr auto;
}

.WdsDropdownMenu__item__detail,
.WdsDropdownMenu__item__label {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
	text-align: left;
}

.WdsDropdownMenu__item:has(.WdsDropdownMenu__item__detail) {
	grid-template-rows: auto auto;
}

.WdsDropdownMenu__item__detail {
	grid-row: 2;
	color: var(--wdsColorGray4);
}

.WdsDropdownMenu__header {
	position: sticky;
	top: 0px;
	padding-top: 8px;
	padding-bottom: 8px;
	background: #fff;

	display: flex;
	flex-direction: column;
	gap: 8px;
}

.WdsDropdownMenu__header__search {
	background-color: var(--wdsColorGray1);
	border-radius: 4px;
	height: 36px;
	width: 100%;

	display: flex;
	align-items: center;
	justify-content: center;
	gap: 4px;

	padding: 8px;
	border: 1px solid transparent;

	color: currentcolor;
}
.WdsDropdownMenu__header__search:hover {
	border-color: var(--wdsColorBlue1);
}
.WdsDropdownMenu__header__search:focus-within {
	background-color: white;
	outline: 4px solid var(--wdsColorBlue1);
}

.WdsDropdownMenu__header__search__input {
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
.WdsDropdownMenu__header__search__input:focus-visible {
	outline: none;
}

.WdsDropdownMenu__header__multiSelect {
	display: flex;
	gap: 12px;
}
.WdsDropdownMenu__header__multiSelect__count,
.WdsDropdownMenu__header__multiSelect__clear {
	text-transform: uppercase;
	font-size: 13px;
}
.WdsDropdownMenu__header__multiSelect__count {
	flex-grow: 1;
	color: var(--wdsColorGray6);
}
.WdsDropdownMenu__header__multiSelect__clear {
	background-color: transparent;
	border: none;
	cursor: pointer;
	text-align: right;
	color: var(--wdsColorGray4);
}
</style>
