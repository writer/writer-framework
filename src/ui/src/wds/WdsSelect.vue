<template>
	<div ref="trigger" class="WdsSelect">
		<!-- use a `<div>` instead of button because Firefox has an issue with draggable `<button>` https://bugzilla.mozilla.org/show_bug.cgi?id=568313 -->
		<div
			class="WdsSelect__trigger"
			:class="{
				'WdsSelect__trigger--placeholder': isPlaceholderSelected,
			}"
			role="button"
			tabindex="0"
			@click="isOpen = !isOpen"
			@keydown.enter="isOpen = !isOpen"
		>
			<template
				v-if="
					(hasUnknowOptionSelected || !hideIcons) &&
					!enableMultiSelection
				"
			>
				<SharedImgWithFallback
					v-if="Array.isArray(currentIcon)"
					:urls="currentIcon"
					:loader-max-width-px="18"
					:loader-max-height-px="18"
				/>
				<WdsIcon v-else :name="currentIcon" />
			</template>
			<div
				v-if="enableMultiSelection"
				class="WdsSelect__trigger__multiSelectLabel"
			>
				<WdsTag
					v-for="option of selectedOptions"
					:key="option.value"
					:text="option.label"
					closable
					@close="handleRemoveValue(option.value)"
				/>
				<p
					v-if="selectedOptions.length === 0"
					class="WdsSelect__trigger__multiSelectLabel__placeholder"
				>
					{{ placeholderLabel }}
				</p>
			</div>
			<div
				v-else
				class="WdsSelect__trigger__label"
				data-writer-tooltip-strategy="overflow"
				:data-writer-tooltip="currentLabel"
			>
				{{ currentLabel ?? placeholderLabel }}
			</div>
			<div class="WdsSelect__trigger__arrow">
				<WdsIcon :name="isOpen ? 'chevron-up' : 'chevron-down'" />
			</div>
		</div>
		<BaseTransitionSlideFade>
			<WdsDropdownMenu
				v-if="isOpen"
				ref="dropdown"
				:enable-search="enableSearch"
				:enable-multi-selection="enableMultiSelection"
				:hide-icons="hideIcons"
				:loading="loading"
				:options="selectOptions"
				:selected="currentValue"
				:style="floatingStyles"
				@select="onSelect"
				@search="updateFloatingStyle"
			/>
		</BaseTransitionSlideFade>
	</div>
</template>

<script lang="ts">
export type { WdsDropdownMenuOption as Option } from "@/wds/WdsDropdownMenu.vue";
</script>

<script setup lang="ts">
import { computed, PropType, ref, useTemplateRef, watch } from "vue";
import { useFloating, autoPlacement } from "@floating-ui/vue";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { useFocusWithin } from "@/composables/useFocusWithin";
import WdsTag from "@/wds/WdsTag.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";
import BaseTransitionSlideFade from "@/components/core/base/BaseTransitionSlideFade.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const WdsDropdownMenu = defineAsyncComponentWithLoader({
	loader: () => import("@/wds/WdsDropdownMenu.vue"),
});

const props = defineProps({
	options: {
		type: Array as PropType<
			WdsDropdownMenuOption[] | Readonly<WdsDropdownMenuOption[]>
		>,
		default: () => [],
	},
	placeholder: { type: String, required: false, default: undefined },
	defaultIcon: { type: String, required: false, default: undefined },
	hideIcons: { type: Boolean, required: false },
	enableSearch: { type: Boolean, required: false },
	enableMultiSelection: { type: Boolean, required: false },
	loading: { type: Boolean, required: false },
	required: { type: Boolean, required: false, default: false },
});

const currentValue = defineModel({
	type: [String, Array] as PropType<string | string[]>,
	required: true,
	default: undefined,
});
const isOpen = ref(false);
const trigger = useTemplateRef("trigger");
const dropdown = useTemplateRef("dropdown");

const middleware = computed(() =>
	// avoid placement on the top when search mode is enabled
	props.enableSearch
		? []
		: [autoPlacement({ allowedPlacements: ["bottom", "top"] })],
);

const { floatingStyles, update: updateFloatingStyle } = useFloating(
	trigger,
	dropdown,
	{
		placement: "bottom",
		middleware,
	},
);

const PLACEHOLDER_VALUE = "";
const placeholderLabel = computed(
	() => props.placeholder ?? "Select an option...",
);

const shouldInjectPlaceholder = computed(
	() => !props.required && !props.enableMultiSelection,
);

const selectOptions = computed<WdsDropdownMenuOption[]>(() => {
	const normalized = (props.options ?? []).map((option) => ({
		...option,
		label:
			option.label ??
			(option.value !== undefined ? String(option.value) : ""),
	}));

	const hasEmptyValueOption = normalized.some(
		(option) => option.value === PLACEHOLDER_VALUE,
	);

	const shouldAddPlaceholder =
		shouldInjectPlaceholder.value && !hasEmptyValueOption;

	if (!shouldAddPlaceholder) {
		return normalized;
	}

	return [
		{
			value: PLACEHOLDER_VALUE,
			label: placeholderLabel.value,
			isPlaceholder: true,
		},
		...normalized.filter((option) => !option.isPlaceholder),
	];
});

const currentValueArray = computed(() => {
	const value = currentValue.value;
	if (value === undefined || value === null) return [];
	const array = Array.isArray(value) ? value : [value];
	return array.filter((v) => v !== undefined && v !== null) as string[];
});

function findOption(value: string | undefined) {
	if (value === undefined) return undefined;
	return selectOptions.value.find((option) => option.value === value);
}

const selectedOptions = computed<WdsDropdownMenuOption[]>(() =>
	currentValueArray.value.map(
		(value) =>
			findOption(value) ?? {
				value,
				label: String(value),
			},
	),
);

const hasUnknowOptionSelected = computed(() =>
	currentValueArray.value.some((value) => !findOption(value)),
);

const currentLabel = computed(() => {
	if (hasUnknowOptionSelected.value) {
		return Array.isArray(currentValue.value)
			? currentValue.value.filter(Boolean).join(" / ")
			: String(currentValue.value ?? "");
	}

	const labels = selectedOptions.value.map((o) => o.label).filter(Boolean);
	if (!labels.length) return undefined;

	const sortedLabels = [...labels].sort((a, b) => a.localeCompare(b));
	return props.enableMultiSelection
		? sortedLabels.join(" / ")
		: sortedLabels[0];
});

const currentIcon = computed(() => {
	if (hasUnknowOptionSelected.value) return "circle-question-mark";
	if (props.hideIcons) return "";
	return (
		selectedOptions.value.at(0)?.icon ??
		props.defaultIcon ??
		"circle-question-mark"
	);
});

const isPlaceholderSelected = computed(() => {
	if (props.enableMultiSelection || props.required) return false;
	return findOption(
		typeof currentValue.value === "string" ? currentValue.value : undefined,
	)?.isPlaceholder;
});

watch(
	[
		selectOptions,
		() => props.required,
		() => props.enableMultiSelection,
		() => currentValue.value,
	],
	ensureValidSelection,
	{ immediate: true },
);

function ensureValidSelection() {
	if (props.enableMultiSelection) return;

	const options = selectOptions.value;
	if (!options.length) return;

	const current = currentValue.value;
	const asString = typeof current === "string" ? current : undefined;
	const hasCurrentSelection =
		asString !== undefined && Boolean(findOption(asString));

	if (props.required) {
		if (!hasCurrentSelection || asString === "") {
			currentValue.value = options[0].value;
		}
		return;
	}

	if (!hasCurrentSelection) {
		currentValue.value = PLACEHOLDER_VALUE;
	}
}

// close the dropdown when clicking outside
const hasFocus = useFocusWithin(trigger);
watch(
	hasFocus,
	() => {
		if (!hasFocus.value) {
			// wait next tick to let event propagate
			setTimeout(() => (isOpen.value = false), 300);
		}
	},
	{ immediate: true },
);

function onSelect(value: string | string[]) {
	if (!props.enableMultiSelection) isOpen.value = false;
	currentValue.value = value;
}

function handleRemoveValue(value: string) {
	if (!Array.isArray(currentValue.value)) return;
	currentValue.value = currentValue.value.filter((v) => v !== value);
}
</script>

<style scoped>
.WdsSelect {
	position: relative;
	user-select: none;
	width: 100%;
	font-size: 0.875rem;
}

.WdsSelect__trigger {
	display: flex;
	align-items: center;
	gap: 8px;

	min-height: 40px;
	width: 100%;
	padding: 8.5px 12px 8.5px 12px;

	border: 1px solid var(--separatorColor);
	border-radius: 8px;

	font-weight: 400;
	font-size: 0.875rem;

	color: var(--primaryTextColor);
	background: var(--wdsColorWhite);

	cursor: pointer;
}
.WdsSelect__trigger:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
	outline: none;
}

.WdsSelect__trigger__label {
	text-overflow: ellipsis;
	overflow: hidden;
	flex-grow: 1;
	text-align: left;
	white-space: nowrap;
}
.WdsSelect__trigger__arrow {
	border: none;
	background-color: transparent;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-weight: 300;
	cursor: pointer;
}
.WdsSelect__trigger--placeholder .WdsSelect__trigger__label {
	color: var(--wdsColorGray4);
}

.WdsSelect__trigger__multiSelectLabel {
	flex-grow: 1;
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-start;
	gap: 8px;
	min-height: 24px;
	line-height: 24px;
}
.WdsSelect__trigger__multiSelectLabel__placeholder {
	color: var(--wdsColorGray5);
}
</style>
