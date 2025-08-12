<template>
	<WdsButton
		class="BaseCollapseIcon"
		:class="{ 'BaseCollapseIcon--collapsed': isCollapsed }"
		variant="tertiary"
		size="icon"
		@click="isCollapsed = !isCollapsed"
	>
		<WdsIcon :name="icon" />
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
import WdsIcon from "@/wds/WdsIcon.vue";
import { computed, PropType } from "vue";

const props = defineProps({
	direction: { type: String as PropType<Direction>, required: true },
});

const isCollapsed = defineModel({ type: Boolean, required: true });

const icon = computed(() => {
	switch (props.direction) {
		case "left-right":
			return "chevron-left";
		case "top-bottom":
			return "chevron-up";
		case "right-left":
			return "chevron-right";
		case "bottom-top":
			return "chevron-down";
		default:
			return "chevron-up";
	}
});
</script>

<style scoped>
.BaseCollapseIcon {
	border-color: var(--separatorColor);
}

.BaseCollapseIcon :deep(svg) {
	transition: all 0.3s ease-in-out;
	transform: rotate(0deg);
}

.BaseCollapseIcon--collapsed :deep(svg) {
	transform: rotate(180deg);
}
</style>
