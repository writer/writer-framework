<template>
	<div ref="trigger" class="SharedCopyClipboardButton">
		<WdsButton
			variant="tertiary"
			size="smallIcon"
			class="button"
			:class="{
				copied,
			}"
			:disabled="!isSupported"
			:aria-label="
				isSingleButtonMode
					? label || 'Copy to clipboard'
					: 'Open options'
			"
			:aria-haspopup="isSingleButtonMode ? undefined : 'menu'"
			:aria-expanded="isSingleButtonMode ? undefined : String(isMenuOpen)"
			:data-writer-tooltip="tooltipMessage"
			data-writer-tooltip-placement="top"
			@click="onCopyButtonClick"
		>
			<WdsIcon :name="copied ? 'check' : 'clipboard'" />
		</WdsButton>
		<WdsDropdownMenu
			v-if="!isSingleButtonMode && isMenuOpen"
			ref="menu"
			class="menu"
			:options="options"
			:style="floatingStyles"
			@select="onMenuItemSelect"
		/>
	</div>
</template>

<script lang="ts">
import type { WdsDropdownMenuOption } from "@/wds/WdsDropdownMenu.vue";

export type SharedCopyClipboardButtonOption = Pick<
	WdsDropdownMenuOption,
	"label" | "value"
>;
</script>

<script setup lang="ts">
import { useClipboard } from "@vueuse/core";
import WdsButton from "@/wds/WdsButton.vue";
import WdsIcon from "@/wds/WdsIcon.vue";
import WdsDropdownMenu from "@/wds/WdsDropdownMenu.vue";
import { computed, nextTick, PropType, ref, useTemplateRef, watch } from "vue";
import { useFloating } from "@floating-ui/vue";
import { useFocusWithin } from "@/composables/useFocusWithin";

const props = defineProps({
	label: { type: String, required: false, default: "" },
	value: { type: String, required: false, default: "" },
	options: {
		type: Array as PropType<SharedCopyClipboardButtonOption[]>,
		required: false,
		default: () => [],
	},
});

const { copy, copied, isSupported } = useClipboard();

const isSingleButtonMode = computed(() => props.options.length === 0);

const tooltipMessage = computed(() => {
	if (!isSingleButtonMode.value) return;
	return copied.value ? "Copied to clipboard" : props.label;
});

const isMenuOpen = ref(false);

const trigger = useTemplateRef("trigger");
const menu = useTemplateRef("menu");

const { floatingStyles } = useFloating(trigger, menu, {
	placement: "bottom-end",
});

// close the menu when clicking outside
const hasFocus = useFocusWithin(trigger);

watch(
	hasFocus,
	() => {
		if (!hasFocus.value) {
			// wait next tick to let event propagate
			nextTick().then(() => {
				isMenuOpen.value = false;
			});
		}
	},
	{
		immediate: true,
	},
);

async function onCopyButtonClick() {
	if (isSingleButtonMode.value) {
		copy(props.value);

		return;
	}

	isMenuOpen.value = true;
}

function onMenuItemSelect(value: string) {
	copy(value);

	isMenuOpen.value = false;
}
</script>

<style scoped>
.SharedCopyClipboardButton {
	position: relative;
}

.menu {
	width: 160px;
}

@keyframes pulse {
	0% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.2);
	}
	100% {
		transform: scale(1);
	}
}

.button.copied :deep(svg) {
	animation: pulse 0.3s ease-in-out;
}

.button.copied {
	color: #4caf50;
}
</style>
