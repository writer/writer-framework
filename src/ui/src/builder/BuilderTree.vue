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
				@click.stop="toggleCollapse(undefined)"
			>
				<i class="material-symbols-outlined">{{
					collapsed ? "expand_more" : "expand_less"
				}}</i>
			</WdsButton>

			<slot name="nameLeft" />
			<span
				class="BuilderTree__main__name"
				:data-writer-tooltip="name"
				data-writer-tooltip-strategy="overflow"
				>{{ name }}</span
			>
			<slot name="nameRight" />
			<div
				v-if="dropdownOptions && isMainHovered"
				class="BuilderTree__main__dropdown"
			>
				<BuilderMoreDropdown
					:options="dropdownOptions"
					trigger-custom-size="16px"
					@select="$emit('dropdownSelect', $event)"
				/>
			</div>
		</div>
		<Transition name="slide-fade">
			<div
				v-show="!collapsed && hasChildren"
				class="BuilderTree__children"
			>
				<slot name="children" />
			</div>
		</Transition>
	</div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, PropType, ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";
import type { Option } from "./BuilderMoreDropdown.vue";
const BuilderMoreDropdown = defineAsyncComponent(
	() => import("./BuilderMoreDropdown.vue"),
);

const props = defineProps({
	name: { type: String, required: true },
	query: { type: String, required: false, default: undefined },
	dataAutomationKey: { type: String, required: false, default: undefined },
	hasChildren: { type: Boolean },
	draggable: { type: Boolean },
	matched: { type: Boolean },
	selected: { type: Boolean },
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

.slide-fade-enter-active {
	transition: all 0.1s ease-out;
}

.slide-fade-leave-active {
	transition: all 0.1s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
	transform: translateY(-18px);
	opacity: 0;
}
@media (prefers-reduced-motion) {
	.slide-fade-enter-from,
	.slide-fade-leave-to,
	.slide-fade-enter-active,
	.slide-fade-leave-active {
		transition: unset;
	}
}

.slide-fade-enter-active {
	transition: all 0.1s ease-out;
}

.slide-fade-leave-active {
	transition: all 0.1s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
	transform: translateY(-18px);
	opacity: 0;
}
@media (prefers-reduced-motion) {
	.slide-fade-enter-from,
	.slide-fade-leave-to,
	.slide-fade-enter-active,
	.slide-fade-leave-active {
		transition: unset;
	}
}
</style>
