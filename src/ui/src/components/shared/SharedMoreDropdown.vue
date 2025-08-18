<template>
	<div ref="trigger" class="SharedMoreDropdown">
		<WdsButton
			:variant="triggerVariant"
			:size="triggerSize"
			:disabled="disabled"
			:custom-size="triggerCustomSize"
			@click.stop="isOpen = !isOpen"
		>
			<WdsIcon :name="triggerIcon" />
		</WdsButton>
		<WdsDropdownMenu
			v-if="isOpen"
			ref="dropdown"
			class="SharedMoreDropdown__dropdown"
			:options="options"
			:style="floatingStyles"
			:hide-icons="hideIcons"
			@select="onSelect"
		/>
	</div>
</template>

<script lang="ts">
export type { WdsDropdownMenuOption as Option } from "@/wds/WdsDropdownMenu.vue";
</script>

<script setup lang="ts">
import { nextTick, PropType, ref, toRef, useTemplateRef, watch } from "vue";
import {
	useFloating,
	autoPlacement,
	Placement,
	Middleware,
} from "@floating-ui/vue";
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";
import { useFocusWithin } from "@/composables/useFocusWithin";
import WdsButton, {
	WdsButtonSize,
	WdsButtonVariant,
} from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import { defineAsyncComponentWithLoader } from "@/utils/defineAsyncComponentWithLoader";

const WdsDropdownMenu = defineAsyncComponentWithLoader({
	loader: () => import("@/wds/WdsDropdownMenu.vue"),
});

const props = defineProps({
	options: {
		type: Array as PropType<WdsDropdownMenuOption[]>,
		default: () => [],
	},
	triggerSize: {
		type: String as PropType<WdsButtonSize>,
		default: "smallIcon",
	},
	triggerVariant: {
		type: String as PropType<WdsButtonVariant>,
		default: "neutral",
	},
	triggerCustomSize: { type: String, default: undefined },
	triggerIcon: { type: String, default: "ellipsis" },
	disabled: { type: Boolean },
	hideIcons: { type: Boolean, required: false },
	dropdownPlacement: {
		type: String as PropType<Placement>,
		required: false,
		default: "bottom-end",
	},
	floatingMiddleware: {
		type: Array as PropType<Middleware[]>,
		required: false,
		default: () => [
			autoPlacement({ allowedPlacements: ["bottom-end", "top-end"] }),
		],
	},
});

// const a : Placement = ''

const emits = defineEmits({
	select: (value: string) => typeof value === "string",
});

const isOpen = ref(false);
const trigger = useTemplateRef("trigger");
const dropdown = useTemplateRef("dropdown");

const { floatingStyles } = useFloating(trigger, dropdown, {
	placement: toRef(props, "dropdownPlacement"),
	middleware: toRef(props, "floatingMiddleware"),
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
	emits("select", value);
}
</script>

<style scoped>
.SharedMoreDropdown {
	position: relative;
}
.SharedMoreDropdown__dropdown {
	min-width: 180px;
}
</style>
