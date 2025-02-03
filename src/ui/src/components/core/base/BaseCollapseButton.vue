<template>
	<WdsButton
		class="BaseCollapseIcon"
		:class="{ 'BaseCollapseIcon--collapsed': isCollapsed }"
		variant="tertiary"
		size="icon"
		@click="isCollapsed = !isCollapsed"
	>
		<i class="BaseCollapseIcon__icon material-symbols-outlined">{{
			icon
		}}</i>
	</WdsButton>
</template>

<script lang="ts">
export type Direction =
	| "left-right"
	| "top-bottom"
	| "bottom-top"
	| "right-left";
</script>

<script setup lang="ts">
import WdsButton from "@/wds/WdsButton.vue";
import { computed, PropType } from "vue";

const props = defineProps({
	direction: { type: String as PropType<Direction>, required: true },
});

const isCollapsed = defineModel({ type: Boolean, required: true });

const icon = computed(() => {
	switch (props.direction) {
		case "left-right":
			return "chevron_left";
		case "top-bottom":
			return "keyboard_arrow_up";
		case "right-left":
			return "chevron_right";
		case "bottom-top":
			return "keyboard_arrow_down";
		default:
			return "keyboard_arrow_up";
	}
});
</script>

<style scoped>
.BaseCollapseIcon {
	border-color: var(--separatorColor);
}

.BaseCollapseIcon__icon {
	transition: all 0.3s ease-in-out;
	transform: rotate(0deg);
}

.BaseCollapseIcon--collapsed .BaseCollapseIcon__icon {
	transform: rotate(180deg);
}
</style>
