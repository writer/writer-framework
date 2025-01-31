<script setup lang="ts">
// TODO(WF-154): to be move in shared
import { onMounted, onUnmounted, PropType, ref } from "vue";

defineProps({
	options: {
		type: Object as PropType<Record<string, string>>,
		required: true,
	},
});

const emits = defineEmits({
	selected: (key: string) => typeof key === "string",
});

/**
 * @deprecated use `useId` from Vue 3.5 when we upgrade
 */
function useId() {
	return Math.random().toString();
}

const trigger = ref<Element>();

const popoverId = useId();
const popover = ref<Element & { hidePopover: () => void }>();
const closePopover = () => popover.value?.hidePopover();

const popoverTop = ref("unset");
const popoverLeft = ref("unset");

function computePopoverPosition() {
	// the popover use an overlay with an absolute position, so we have to positionate it manually according to the trigger position
	const boundingRect = trigger.value.getBoundingClientRect();
	popoverTop.value = `${boundingRect.top + boundingRect.height + 4 + window.pageYOffset}px`;
	popoverLeft.value = `${boundingRect.left + window.pageXOffset}px`;
}

function onItemClick(key: string) {
	emits("selected", key);
	closePopover();
}

onMounted(() => window.addEventListener("scroll", closePopover));
onUnmounted(() => window.removeEventListener("scroll", closePopover));
</script>

<template>
	<div class="BaseDropdown">
		<button
			ref="trigger"
			:popovertarget="popoverId"
			class="BaseDropdown__trigger"
			@click="computePopoverPosition"
		>
			<i class="material-symbols-outlined">more_horiz</i>
		</button>
		<div
			:id="popoverId"
			ref="popover"
			class="BaseDropdown__dropdown"
			popover
			:style="{ top: popoverTop, left: popoverLeft }"
		>
			<button
				v-for="[key, value] of Object.entries(options)"
				:key="key"
				class="BaseDropdown__dropdown_item"
				tabindex="1"
				@click.capture="onItemClick(key)"
			>
				{{ value }}
			</button>
		</div>
	</div>
</template>

<style scoped>
.BaseDropdown {
	position: relative;
}

.BaseDropdown__trigger {
	cursor: pointer;
	background-color: transparent;
	border: none;
	height: 16px;
	width: 16px;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.BaseDropdown__dropdown {
	position: absolute;
	z-index: 1;
	top: 18px;
	transform: translateX(calc(-100% + 18px));
	background-color: white;

	flex-direction: column;

	min-width: 120px;
	margin: 0;

	border-radius: 4px;
	border: 1px solid var(--separatorColor);
	box-shadow: var(--containerShadow);
}
.BaseDropdown__dropdown:popover-open {
	display: flex;
}

.BaseDropdown__dropdown_item {
	/* reset button */
	background-color: transparent;
	border: none;

	text-align: left;

	padding: 8px 16px;
	border-bottom: 1px solid var(--separatorColor);
	cursor: pointer;
}
.BaseDropdown__dropdown_item:focus {
	outline-offset: -2px;
}
.BaseDropdown__dropdown_item:hover {
	background-color: var(--separatorColor);
}
.BaseDropdown__dropdown_item:last-child {
	border-bottom: unset;
}
</style>
