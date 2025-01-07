<template>
	<div class="BuilderTree">
		<div
			class="BuilderTree__main"
			:class="{ selected, notMatched, childless }"
			tabindex="0"
			:draggable="draggable"
			:data-automation-key="dataAutomationKey"
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
				@click.stop="toggleCollapse"
			>
				<i class="material-symbols-outlined">{{
					collapsed ? "expand_more" : "expand_less"
				}}</i>
			</WdsButton>

			<slot name="nameLeft" />
			<span class="BuilderTree__main__name">{{ name }}</span>
			<slot name="nameRight" />
		</div>
		<div
			v-show="(!collapsed || props.query) && hasChildren"
			class="BuilderTree__children"
		>
			<slot name="children" />
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import WdsButton from "@/wds/WdsButton.vue";

const props = defineProps({
	name: { type: String, required: true },
	query: { type: String, required: false, default: undefined },
	dataAutomationKey: { type: String, required: false, default: undefined },
	hasChildren: { type: Boolean },
	draggable: { type: Boolean },
	matched: { type: Boolean },
	selected: { type: Boolean },
});

const emit = defineEmits({
	expandBranch: () => true,
	select: (ev: MouseEvent | KeyboardEvent) => !!ev,
	dragover: (ev: DragEvent) => !!ev,
	dragstart: (ev: DragEvent) => !!ev,
	dragend: (ev: DragEvent) => !!ev,
	drop: (ev: DragEvent) => !!ev,
});

defineExpose({ expand });

const collapsed = ref(false);

const notMatched = computed(() => !props.matched);

const childless = computed(() => !props.hasChildren);

function expand() {
	collapsed.value = false;
	emit("expandBranch");
}

function toggleCollapse() {
	collapsed.value = !collapsed.value;
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
	overflow: hidden;
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
</style>
