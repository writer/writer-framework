<script setup lang="ts">
import { computed } from "vue";
import CoreDataFrameCellNumber from "./CoreDataframeCellNumber.vue";
import CoreDataFrameCellText from "./CoreDataframeCellText.vue";
import CoreDataFrameCellBoolean from "./CoreDataframeCellBoolean.vue";
import CoreDataframeCellUnknown from "./CoreDataframeCellUnknown.vue";

const props = defineProps({
	value: { validator: () => true, required: true },
	useMarkdown: { type: Boolean, required: false },
	editable: { type: Boolean, required: false },
	wrapText: { type: Boolean, required: false },
});

defineEmits({
	change: (value: unknown) => value !== undefined,
});

const component = computed(() => {
	switch (typeof props.value) {
		case "number":
		case "bigint":
			return CoreDataFrameCellNumber;
		case "boolean":
			return CoreDataFrameCellBoolean;
		case "string":
			return CoreDataFrameCellText;
		default:
			return CoreDataframeCellUnknown;
	}
});
</script>

<template>
	<component
		:is="component"
		:value="value"
		:use-markdown="useMarkdown"
		:editable="editable"
		:wrap-text="wrapText"
		@change="$emit('change', $event)"
	/>
</template>
