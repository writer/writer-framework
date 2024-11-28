<template>
	<div ref="trigger" class="BuilderSelect">
		<button
			class="BuilderSelect__trigger"
			role="button"
			@click="isOpen = !isOpen"
		>
			<i v-if="!hideIcons" class="material-symbols-outlined">{{
				currentIcon
			}}</i>
			<div class="BuilderSelect__trigger__label">{{ currentLabel }}</div>
			<div class="BuilderSelect__trigger__arrow">
				<i class="material-symbols-outlined">{{ expandIcon }}</i>
			</div>
		</button>
		<WdsMenu
			v-if="isOpen"
			ref="dropdown"
			:enable-search="enableSearch"
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
	watch,
} from "vue";
import { useFloating, autoPlacement } from "@floating-ui/vue";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import { useFocusWithin } from "@/composables/useFocusWithin";

const WdsMenu = defineAsyncComponent(() => import("@/wds/WdsDropdownMenu.vue"));

const props = defineProps({
	options: {
		type: Array as PropType<WdsDropdownMenuOption[]>,
		default: () => [],
	},
	defaultIcon: { type: String, required: false, default: undefined },
	hideIcons: { type: Boolean, required: false },
	enableSearch: { type: Boolean, required: false },
});

const currentValue = defineModel({ type: String, required: false });
const isOpen = ref(false);
const trigger = ref<HTMLElement>();
const dropdown = ref<HTMLElement>();

const { floatingStyles, update: updateFloatingStyle } = useFloating(
	trigger,
	dropdown,
	{
		placement: "bottom",
		middleware: [autoPlacement()],
	},
);

const expandIcon = computed(() =>
	isOpen.value ? "keyboard_arrow_up" : "expand_more",
);

const selectedOption = computed(() =>
	props.options.find((o) => o.value === currentValue.value),
);

const currentLabel = computed(() => selectedOption.value?.label ?? "");

const currentIcon = computed(() => {
	if (props.hideIcons) return "";
	return selectedOption.value?.icon ?? props.defaultIcon ?? "help_center";
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

function onSelect(value: string) {
	isOpen.value = false;
	currentValue.value = value;
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

	height: 40px;
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
.BuilderSelect__trigger__label {
	text-overflow: ellipsis;
	overflow: hidden;
	flex-grow: 1;
	text-align: left;
}
.BuilderSelect__trigger__arrow {
	border: none;
	background-color: transparent;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-weight: 300;
	color: #000000e6;
	cursor: pointer;
}
</style>
