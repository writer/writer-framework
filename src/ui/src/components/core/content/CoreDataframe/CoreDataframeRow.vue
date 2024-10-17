<template>
	<div
		class="CoreDataframeRow"
		tabindex="0"
		@mouseover="isRowHovered = true"
		@mouseleave="isRowHovered = false"
		@focusin="isRowHovered = true"
	>
		<div v-if="hasActions" class="CoreDataframeRow__hand">
			<BaseDropdown
				v-if="isRowHovered"
				:options="actions"
				@selected="$emit('action', $event, row[ARQUERO_INTERNAL_ID])"
			/>
		</div>
		<div v-if="showIndex" class="cell indexCell">{{ indexText }}</div>
		<CoreDataframeCell
			v-for="columnName in columns"
			:key="`${row[ARQUERO_INTERNAL_ID]}_${columnName}`"
			class="cell"
			:value="row[columnName]"
			:use-markdown="useMarkdown"
			:editable="editable"
			@change="
				$emit('change', columnName, row[ARQUERO_INTERNAL_ID], $event)
			"
		/>
	</div>
</template>

<script setup lang="ts">
import { computed, PropType, ref } from "vue";
import CoreDataframeCell from "./CoreDataframeCell.vue";
import BaseDropdown from "../../base/BaseDropdown.vue";
import { ARQUERO_INTERNAL_ID } from "./constants";

const props = defineProps({
	showIndex: { type: Boolean, required: false },
	indexText: { type: [Number, String], required: true },
	columns: { type: Array as PropType<string[]>, required: true },
	row: { type: Object, required: true },
	useMarkdown: { type: Boolean, required: false },
	editable: { type: Boolean, required: false },
	actions: {
		type: Object as PropType<Record<string, string>>,
		required: true,
	},
});

defineEmits({
	change: (columnName: string, id: number, value: unknown) =>
		typeof columnName === "string" &&
		typeof id === "number" &&
		value !== undefined,
	action: (action: string, index: number) =>
		typeof index === "number" && typeof action === "string",
});

const isRowHovered = ref(false);

const hasActions = computed(() => Object.keys(props.actions || {}).length > 0);
</script>

<style scoped>
.CoreDataframeRow {
	display: grid;
	/* the parent will apply `grid-template-columns` */
	position: relative;
}

.CoreDataframeRow__hand {
	display: flex;
	align-items: center;
	justify-content: center;
}
</style>
