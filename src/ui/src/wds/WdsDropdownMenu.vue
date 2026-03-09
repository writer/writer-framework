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
					type="button"
					@click="$emit('select', [])"
				>
					Clear all
				</button>
			</div>
			<div
				v-if="enableSearch"
				class="WdsDropdownMenu__header__search"
				:class="{
					'WdsDropdownMenu__header__search--no-results': hasNoResults,
				}"
			>
				<WdsIcon name="search" />
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

		<div v-else-if="hasNoResults" class="WdsDropdownMenu__no-results">
			No results
		</div>
		<template v-else>
			<template v-for="option in optionsFiltered" :key="option.value">
				<!-- Divider -->
				<div
					v-if="option.type === 'divider'"
					class="WdsDropdownMenu__divider"
				/>
				<!-- Header -->
				<div
					v-else-if="option.type === 'header'"
					class="WdsDropdownMenu__sectionHeader"
				>
					{{ option.label }}
				</div>
				<!-- Regular or Checkbox items -->
				<SharedLazyLoader v-else>
					<template #spinner>
						<div class="WdsDropdownMenu__itemLazyLoader">
							<WdsSkeletonLoader />
						</div>
					</template>
					<template #content>
						<!-- Switch type option -->
						<div
							v-if="option.type === 'switch'"
							role="menuitemcheckbox"
							:aria-checked="option.checked ?? false"
							:aria-disabled="option.disabled"
							class="WdsDropdownMenu__switchItem"
							:class="{
								'WdsDropdownMenu__switchItem--disabled':
									option.disabled,
							}"
							:data-automation-key="option.value"
							tabindex="0"
							@click.stop="
								!option.disabled && onSelect(option.value)
							"
							@keydown.enter.prevent="
								!option.disabled && onSelect(option.value)
							"
							@keydown.space.prevent="
								!option.disabled && onSelect(option.value)
							"
						>
							<div class="WdsDropdownMenu__switchItem__content">
								<div class="WdsDropdownMenu__switchItem__label">
									{{ option.label }}
								</div>
								<div
									v-if="option.detail"
									class="WdsDropdownMenu__switchItem__detail"
								>
									{{ option.detail }}
								</div>
							</div>
							<WdsSwitch
								:model-value="option.checked ?? false"
								:disabled="option.disabled"
								:aria-hidden="true"
								tabindex="-1"
								@click.stop.prevent
							/>
						</div>
						<!-- Multi-selection checkbox -->
						<WdsCheckbox
							v-else-if="enableMultiSelection"
							class="WdsDropdownMenu__checkbox"
							:checked="isSelected(option.value)"
							:label="option.label"
							:detail="option.detail"
							:data-automation-key="option.value"
							:disabled="option.disabled"
							:model-value="isSelected(option.value)"
							@update:model-value="onSelect(option.value)"
						/>
						<!-- Regular menu item -->
						<WdsDropdownMenuItem
							v-else
							:option="option"
							:data-automation-key="option.value"
							:selected="isSelected(option.value)"
							@click.stop="onSelect(option.value)"
						/>
					</template>
				</SharedLazyLoader>
			</template>
		</template>
	</div>
</template>

<script lang="ts">
export type WdsDropdownMenuOptionBase = {
	value: string;
	label: string;
	detail?: string;
	shortcut?: string;
	/**
	 * A font icon or an array of image URL
	 */
	icon?: string | string[];
	iconColor?: string;
	iconBgColor?: string;
	disabled?: boolean;
	variant?: "danger";
};

export type WdsDropdownMenuOptionRegular = WdsDropdownMenuOptionBase & {
	type?: "regular";
};

export type WdsDropdownMenuOptionSwitch = WdsDropdownMenuOptionBase & {
	type: "switch";
	checked?: boolean;
};

export type WdsDropdownMenuOptionDivider = {
	type: "divider";
	value: string; // unique key for v-for
};

export type WdsDropdownMenuOptionHeader = {
	type: "header";
	value: string; // unique key for v-for
	label: string;
};

export type WdsDropdownMenuOption =
	| WdsDropdownMenuOptionRegular
	| WdsDropdownMenuOptionSwitch
	| WdsDropdownMenuOptionDivider
	| WdsDropdownMenuOptionHeader;
</script>

<script setup lang="ts">
// from https://www.figma.com/design/jgLDtwVwg3hReC1t4Vw20D/.WDS-Writer-Design-System?node-id=128-396&t=9Gy9MYDycjVV8C2Y-1
import { computed, PropType, ref, watch } from "vue";
import WdsIcon from "./WdsIcon.vue";
import WdsSkeletonLoader from "./WdsSkeletonLoader.vue";
import WdsCheckbox from "./WdsCheckbox.vue";
import WdsSwitch from "./WdsSwitch.vue";
import WdsDropdownMenuItem from "./WdsDropdownMenuItem.vue";
import SharedLazyLoader from "@/components/shared/SharedLazyLoader.vue";

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
	return props.options.filter((option) => {
		if (option.type === "divider" || option.type === "header") {
			return true;
		}
		return (
			option.label.toLowerCase().includes(query) ||
			option.detail?.toLowerCase().includes(query)
		);
	});
});

const hasNoResults = computed(() => {
	return (
		props.enableSearch &&
		searchTerm.value.trim() !== "" &&
		optionsFiltered.value.length === 0 &&
		!props.loading
	);
});

function isSelected(value: string) {
	return Array.isArray(props.selected)
		? props.selected.includes(value)
		: props.selected === value;
}

const optionsValues = computed(() => {
	return new Set(
		props.options
			.filter((o) => o.type !== "divider" && o.type !== "header")
			.map((o) => o.value),
	);
});

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

.WdsDropdownMenu__itemLazyLoader {
	padding: 12px;
}

.WdsDropdownMenu__header {
	position: sticky;
	top: 0;
	padding-top: 8px;
	padding-bottom: 8px;
	background: #fff;

	display: flex;
	flex-direction: column;
	gap: 8px;
	z-index: 2;
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

.WdsDropdownMenu__header__search--no-results {
	border-color: var(--wdsColorOrange2, #e53e3e) !important;
}
.WdsDropdownMenu__header__search--no-results:hover {
	border-color: var(--wdsColorOrange2, #e53e3e) !important;
}
.WdsDropdownMenu__header__search--no-results:focus-within {
	border-color: var(--wdsColorOrange2, #e53e3e) !important;
	outline: 4px solid rgba(229, 62, 62, 0.2) !important;
}

.WdsDropdownMenu__no-results {
	padding: 12px;
	text-align: center;
	color: var(--wdsColorGray5, #6b7280);
	font-size: 0.875rem;
}

.WdsDropdownMenu__divider {
	border-top: 1px solid var(--wdsColorGray2);
	margin: 8px 0;
}

.WdsDropdownMenu__sectionHeader {
	text-transform: uppercase;
	font-size: 13px;
	font-weight: 500;
	color: var(--wdsColorGray6);
	padding: 12px 8px 8px 8px;
	margin-top: 4px;
}

.WdsDropdownMenu__switchItem {
	background-color: transparent;
	border: none;
	display: flex;
	width: 100%;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
	border-radius: 4px;
	padding: 8px;
	cursor: pointer;
	transition: background-color 0.2s;
	min-height: 36px;
}

.WdsDropdownMenu__switchItem:hover:not(.WdsDropdownMenu__switchItem--disabled) {
	background-color: var(--wdsColorGray1);
}

.WdsDropdownMenu__switchItem--disabled {
	opacity: 0.4;
	cursor: not-allowed;
}

.WdsDropdownMenu__switchItem__content {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 2px;
	flex: 1;
	text-align: left;
}

.WdsDropdownMenu__switchItem__label {
	font-weight: 400;
	font-size: 0.75rem;
	color: var(--wdsColorGray6);
}

.WdsDropdownMenu__switchItem__detail {
	font-size: 0.6875rem;
	color: var(--wdsColorGray5);
}
</style>
