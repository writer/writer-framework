<template>
	<div class="BuilderTree">
		<div
			class="BuilderTree__main"
			:class="{ selected, notMatched, childless }"
			tabindex="0"
			:draggable="draggable"
			:data-automation-key="dataAutomationKey"
			:aria-expanded="!collapsed"
			@mouseenter="isMainHovered = true"
			@mouseleave="isMainHovered = false"
			@click="$emit('select', $event)"
			@keydown.enter="$emit('select', $event)"
			@dragover="$emit('dragover', $event)"
			@dragstart="$emit('dragstart', $event)"
			@dragend="$emit('dragend', $event)"
			@drop="$emit('drop', $event)"
		>
			<WdsButton
				v-if="hasChildren"
				class="BuilderTree__main__collapser"
				variant="neutral"
				size="icon"
				:disabled="disabled"
				@click.stop="toggleCollapse(undefined)"
			>
				<i class="material-symbols-outlined">{{
					collapsed ? "expand_more" : "expand_less"
				}}</i>
			</WdsButton>

			<slot name="nameLeft" />
			<span
				class="BuilderTree__main__name"
				:class="{
					'BuilderTree__main__name--disabled': disabled,
					'BuilderTree__main__name--root': variant === 'root',
				}"
				:data-writer-tooltip="name"
				data-writer-tooltip-strategy="overflow"
				>{{ name }}</span
			>
			<slot name="nameRight" />
			<div
				v-if="dropdownOptions && isMainHovered"
				class="BuilderTree__main__dropdown"
			>
				<SharedMoreDropdown
					:options="dropdownOptions"
					trigger-custom-size="16px"
					@select="$emit('dropdownSelect', $event)"
				/>
			</div>
		</div>
		<BaseTransitionSlideFade>
			<div
				v-show="!collapsed && hasChildren"
				class="BuilderTree__children"
				:class="{
					'BuilderTree__children--noNestedSpace': noNestedSpace,
				}"
			>
				<slot name="children" />
			</div>
		</BaseTransitionSlideFade>
	</div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, PropType, ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import type { Option } from "@/components/shared/SharedMoreDropdown.vue";
import BaseTransitionSlideFade from "@/components/core/base/BaseTransitionSlideFade.vue";
const SharedMoreDropdown = defineAsyncComponent(
	() => import("@/components/shared/SharedMoreDropdown.vue"),
);

const props = defineProps({
	name: { type: String, required: true },
	query: { type: String, required: false, default: undefined },
	variant: {
		type: String as PropType<"root">,
		required: false,
		default: undefined,
	},
	noNestedSpace: {
		type: Boolean,
		required: false,
	},
	dataAutomationKey: { type: String, required: false, default: undefined },
	hasChildren: { type: Boolean },
	draggable: { type: Boolean },
	matched: { type: Boolean },
	selected: { type: Boolean },
	disabled: { type: Boolean },
	dropdownOptions: {
		type: Array as PropType<Option[]>,
		required: false,
		default: undefined,
	},
});

const emit = defineEmits({
	expandBranch: () => true,
	select: (ev: MouseEvent | KeyboardEvent) => !!ev,
	dragover: (ev: DragEvent) => !!ev,
	dragstart: (ev: DragEvent) => !!ev,
	dragend: (ev: DragEvent) => !!ev,
	drop: (ev: DragEvent) => !!ev,
	dropdownSelect: (key: string) => typeof key === "string",
});

defineExpose({ expand, toggleCollapse });

const collapsed = ref(false);
const isMainHovered = ref(false);

const notMatched = computed(() => !props.matched);

const childless = computed(() => !props.hasChildren);

function expand() {
	collapsed.value = false;
	emit("expandBranch");
}

function toggleCollapse(newCollapse?: boolean) {
	newCollapse ??= !collapsed.value;
	if (newCollapse !== collapsed.value) collapsed.value = newCollapse;
}
</script>

<style scoped>
.BuilderTree {
	font-size: 12px;
}

.BuilderTree__main {
	padding: 8px;
	border-radius: 8px;
	cursor: pointer;
	display: flex;
	flex-wrap: nowrap;
	text-wrap: nowrap;
	max-width: 100%;
	align-items: center;
	outline: none;
	gap: 4px;
	color: var(--builderSecondaryTextColor);
}

.BuilderTree__main.childless {
	padding-left: 12px;
}

.BuilderTree__main:focus {
	outline: 1px solid var(--builderSelectedColor);
}

.BuilderTree__main:hover {
	background: var(--builderSubtleSeparatorColor);
}

.BuilderTree__main.selected {
	background: var(--builderSelectedColor);
}

.BuilderTree__main.notMatched {
	filter: opacity(0.2);
}

.BuilderTree__main__name {
	color: var(--builderPrimaryTextColor);
	text-overflow: ellipsis;
	overflow: hidden;
}
.BuilderTree__main__name--disabled {
	color: var(--wdsColorGray6);
}

.BuilderTree__main__collapser {
	margin-left: -4px;
	width: 20px;
	height: 20px;
}

.BuilderTree__children {
	margin-left: 20px;
}

.BuilderTree__main__dropdown {
	flex-grow: 1;
	display: flex;
	justify-content: flex-end;
}

.BuilderTree__main__name--root {
	font-weight: 500;
	text-transform: uppercase;
}
.BuilderTree__children--noNestedSpace {
	margin-left: unset;
}
</style>
