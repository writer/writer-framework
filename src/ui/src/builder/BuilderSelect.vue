<template>
	<div ref="trigger" class="BuilderSelect">
		<button
			class="BuilderSelect__trigger"
			role="button"
			@click="isOpen = !isOpen"
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
				/>
				<i v-else class="material-symbols-outlined">{{
					currentIcon
				}}</i>
			</template>
			<div
				v-if="enableMultiSelection"
				class="BuilderSelect__trigger__multiSelectLabel"
			>
				<WdsTag
					v-for="option of selectedOptions"
					:key="option.value"
					:text="option.label"
					closable
					@close="handleRemoveValue(option.value)"
				/>
			</div>
			<div
				v-else
				class="BuilderSelect__trigger__label"
				data-writer-tooltip-strategy="overflow"
				:data-writer-tooltip="currentLabel"
			>
				{{ currentLabel }}
			</div>
			<div class="BuilderSelect__trigger__arrow">
				<i class="material-symbols-outlined">{{ expandIcon }}</i>
			</div>
		</button>
		<WdsDropdownMenu
			v-if="isOpen"
			ref="dropdown"
			:enable-search="enableSearch"
			:enable-multi-selection="enableMultiSelection"
			:hide-icons="hideIcons"
			:loading="loading"
			:options="options"
			:selected="currentValue"
			:style="floatingStyles"
			@select="onSelect"
			@search="updateFloatingStyle"
		/>
	</div>
</template>

<script lang="ts">
export type { WdsDropdownMenuOption as Option } from "@/wds/WdsDropdownMenu.vue";
</script>

<script setup lang="ts">
import {
	computed,
	defineAsyncComponent,
	nextTick,
	PropType,
	ref,
	useTemplateRef,
	watch,
} from "vue";
import { useFloating, autoPlacement } from "@floating-ui/vue";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import { useFocusWithin } from "@/composables/useFocusWithin";
import WdsTag from "@/wds/WdsTag.vue";
import SharedImgWithFallback from "@/components/shared/SharedImgWithFallback.vue";

const WdsDropdownMenu = defineAsyncComponent(
	() => import("@/wds/WdsDropdownMenu.vue"),
);

const props = defineProps({
	options: {
		type: Array as PropType<
			WdsDropdownMenuOption[] | Readonly<WdsDropdownMenuOption[]>
		>,
		default: () => [],
	},
	defaultIcon: { type: String, required: false, default: undefined },
	hideIcons: { type: Boolean, required: false },
	enableSearch: { type: Boolean, required: false },
	enableMultiSelection: { type: Boolean, required: false },
	loading: { type: Boolean, required: false },
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

const expandIcon = computed(() =>
	isOpen.value ? "keyboard_arrow_up" : "expand_more",
);

const currentValueArray = computed(() => {
	if (!currentValue.value) return [];
	const array = Array.isArray(currentValue.value)
		? currentValue.value
		: [currentValue.value];
	return array.filter(Boolean);
});

const selectedOptions = computed<WdsDropdownMenuOption[]>(() =>
	currentValueArray.value.map(
		(v) =>
			props.options.find((o) => o.value === v) ?? { value: v, label: v },
	),
);

const hasUnknowOptionSelected = computed(() => {
	return (
		currentValue.value &&
		!props.options.some((o) => o.value === currentValue.value)
	);
});

const currentLabel = computed(() => {
	if (hasUnknowOptionSelected.value) return String(currentValue.value);

	return selectedOptions.value
		.map((o) => o.label)
		.sort()
		.join(" / ");
});

const currentIcon = computed(() => {
	if (hasUnknowOptionSelected.value) return "help_center";
	if (props.hideIcons) return "";
	return (
		selectedOptions.value.at(0)?.icon ?? props.defaultIcon ?? "help_center"
	);
});

// close the dropdown when clicking outside
const hasFocus = useFocusWithin(trigger);
watch(
	hasFocus,
	() => {
		if (!hasFocus.value) {
			// wait next tick to let event propagate
			nextTick().then(() => (isOpen.value = false));
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
.BuilderSelect {
	position: relative;
	user-select: none;
	width: 100%;
	font-size: 0.875rem;
}

.BuilderSelect__trigger {
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
	background: transparent;

	cursor: pointer;
}
.BuilderSelect__trigger:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
	outline: none;
}
.BuilderSelect__trigger__label {
	text-overflow: ellipsis;
	overflow: hidden;
	flex-grow: 1;
	text-align: left;
	white-space: nowrap;
}
.BuilderSelect__trigger__arrow {
	border: none;
	background-color: transparent;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-weight: 300;
	cursor: pointer;
}

.BuilderSelect__trigger__multiSelectLabel {
	flex-grow: 1;

	display: flex;
	flex-wrap: wrap;
	justify-content: flex-start;
	gap: 8px;
}
</style>
